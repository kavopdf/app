import com.kavopdf.app.engine.Stalls;

/**
 * The main-thread watchdog. These cases come straight out of the activity logs.
 */
public class TestStalls {
    static int pass = 0, fail = 0;
    static void check(String what, boolean ok) {
        if (ok) { pass++; System.out.println("  PASS  " + what); }
        else { fail++; System.out.println("  FAIL  " + what); }
    }

    public static void main(String[] a) {
        // --- a healthy foreground beat is silent -------------------------------------
        Stalls s = new Stalls();
        long t = 0;
        s.onTick(t, Stalls.TICK_MS);
        boolean quiet = true;
        for (int i = 0; i < 20; i++) {
            t += Stalls.TICK_MS;
            if (s.onTick(t, Stalls.TICK_MS) != 0) quiet = false;
        }
        check("a steady 500ms beat never reports", quiet);

        // --- THE LOG BUG: the ticker backs off to 5s behind another app ---------------
        Stalls b = new Stalls();
        t = 0;
        b.onTick(t, Stalls.TICK_MS);
        t += Stalls.TICK_MS;
        b.onTick(t, Stalls.TICK_MS);
        t += Stalls.IDLE_MS;                       // the ticker was rescheduled at 5s
        long got = b.onTick(t, Stalls.IDLE_MS);
        check("a 5001ms gap that was SCHEDULED as 5000ms is not a block (got " + got + ")", got == 0L);

        // --- a steady idle beat is silent too ---------------------------------------
        Stalls i = new Stalls();
        t = 0;
        i.onTick(t, Stalls.IDLE_MS);
        quiet = true;
        for (int k = 0; k < 10; k++) {
            t += Stalls.IDLE_MS;
            if (i.onTick(t, Stalls.IDLE_MS) != 0) quiet = false;
        }
        check("a steady 5000ms idle beat never reports", quiet);

        // --- a real block is still caught --------------------------------------------
        Stalls r = new Stalls();
        t = 0;
        r.onTick(t, Stalls.TICK_MS);
        t += 6000;                                  // scheduled 500, arrived 6000
        got = r.onTick(t, Stalls.TICK_MS);
        check("a 6000ms gap on a 500ms beat reports ~5500ms (got " + got + ")", got == 5500L);

        // --- one entry per block ------------------------------------------------------
        t += 6000;
        check("the same block is not reported twice", r.onTick(t, Stalls.TICK_MS) == 0L);

        // --- a healthy beat after a block re-arms the detector ------------------------
        t += Stalls.TICK_MS;
        r.onTick(t, Stalls.TICK_MS);
        t += 6000;
        check("a new block after a healthy beat is reported again", r.onTick(t, Stalls.TICK_MS) > 0L);

        // --- timers suspended for a long time is not a block -------------------------
        Stalls d = new Stalls();
        t = 0;
        d.onTick(t, Stalls.TICK_MS);
        t += 45_000;
        check("a 45s suspension reports nothing", d.onTick(t, Stalls.TICK_MS) == 0L);

        // --- reset clears the beat ----------------------------------------------------
        Stalls z = new Stalls();
        z.onTick(0, Stalls.TICK_MS);
        z.onTick(9000, Stalls.TICK_MS);
        z.reset();
        check("after reset the first tick is silent", z.onTick(50_000, Stalls.TICK_MS) == 0L);

        // --- a block smaller than BLOCK_MS is noise -----------------------------------
        Stalls n = new Stalls();
        n.onTick(0, Stalls.TICK_MS);
        check("a 1.5s hiccup on a 500ms beat is quiet",
                n.onTick(2000, Stalls.TICK_MS) == 0L);

        // --- the old one-argument call still beats at TICK_MS -------------------------
        Stalls o = new Stalls();
        o.onTick(0);
        check("the one-argument onTick still measures against TICK_MS",
                o.onTick(6000) == 5500L);

        System.out.println("STALLS TOTAL: " + pass + " passed, " + fail + " failed");
        if (fail > 0) System.exit(1);
    }
}
