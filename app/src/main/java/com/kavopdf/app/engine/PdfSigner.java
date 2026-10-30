package com.kavopdf.app.engine;

import com.tom_roush.pdfbox.pdmodel.PDDocument;
import com.tom_roush.pdfbox.pdmodel.interactive.digitalsignature.PDSignature;
import com.tom_roush.pdfbox.pdmodel.interactive.digitalsignature.SignatureInterface;

import org.bouncycastle.asn1.x509.BasicConstraints;
import org.bouncycastle.asn1.x509.Extension;
import org.bouncycastle.asn1.x509.KeyUsage;
import org.bouncycastle.cert.X509CertificateHolder;
import org.bouncycastle.cert.jcajce.JcaCertStore;
import org.bouncycastle.cert.jcajce.JcaX509CertificateConverter;
import org.bouncycastle.cert.jcajce.JcaX509v3CertificateBuilder;
import org.bouncycastle.cms.CMSProcessableByteArray;
import org.bouncycastle.cms.CMSSignedData;
import org.bouncycastle.cms.CMSSignedDataGenerator;
import org.bouncycastle.cms.SignerInformation;
import org.bouncycastle.cms.SignerInformationStore;
import org.bouncycastle.cms.jcajce.JcaSignerInfoGeneratorBuilder;
import org.bouncycastle.cms.jcajce.JcaSimpleSignerInfoVerifierBuilder;
import org.bouncycastle.operator.ContentSigner;
import org.bouncycastle.operator.jcajce.JcaContentSignerBuilder;
import org.bouncycastle.operator.jcajce.JcaDigestCalculatorProviderBuilder;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.math.BigInteger;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.PrivateKey;
import java.security.SecureRandom;
import java.security.cert.X509Certificate;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Locale;

import javax.security.auth.x500.X500Principal;

/**
 * Real, cryptographic PDF digital signatures (PKCS#7 / CMS detached) plus
 * independent verification. This is the same class of signature Adobe Reader
 * reports as "Signed" — not a picture of a signature.
 */
public final class PdfSigner {

    private PdfSigner() { }

    public static final class SignParams {
        public String name = "";
        public String organisation = "";
        public String reason = "";
        public String location = "";
        public String contact = "";
    }

    public static final class SignatureInfo {
        public String signerName = "";
        public String subject = "";
        public String issuer = "";
        public String reason = "";
        public String location = "";
        public String contact = "";
        public String date = "";
        /** The CMS signature verified against the signed bytes (integrity + signer). */
        public boolean valid;
        /** The signature covers the whole file (nothing appended after signing). */
        public boolean coversWholeDocument;
        public String error = "";
    }

    // ---------------------------------------------------------------------
    // Signing
    // ---------------------------------------------------------------------

    public static void sign(File src, File out, SignParams p) throws Exception {
        KeyPair keyPair = generateKeyPair();
        X509Certificate cert = selfSigned(keyPair, p.name, p.organisation);

        try (PDDocument doc = PDDocument.load(src)) {
            PDSignature sig = new PDSignature();
            sig.setFilter(PDSignature.FILTER_ADOBE_PPKLITE);
            sig.setSubFilter(PDSignature.SUBFILTER_ADBE_PKCS7_DETACHED);
            sig.setName(p.name == null || p.name.isEmpty() ? "KavoPDF signer" : p.name);
            if (p.reason != null && !p.reason.isEmpty()) sig.setReason(p.reason);
            if (p.location != null && !p.location.isEmpty()) sig.setLocation(p.location);
            if (p.contact != null && !p.contact.isEmpty()) sig.setContactInfo(p.contact);
            sig.setSignDate(Calendar.getInstance());

            final PrivateKey key = keyPair.getPrivate();
            final X509Certificate certificate = cert;
            doc.addSignature(sig, new SignatureInterface() {
                @Override
                public byte[] sign(InputStream content) throws IOException {
                    return cmsSign(readAll(content), key, certificate);
                }
            });

            try (FileOutputStream fos = new FileOutputStream(out)) {
                doc.saveIncremental(fos);
            }
        }
    }

    // ---------------------------------------------------------------------
    // Verification
    // ---------------------------------------------------------------------

    public static List<SignatureInfo> verify(File src) throws Exception {
        List<SignatureInfo> result = new ArrayList<>();
        try (PDDocument doc = PDDocument.load(src)) {
            List<PDSignature> sigs = doc.getSignatureDictionaries();
            for (PDSignature sig : sigs) {
                SignatureInfo info = new SignatureInfo();
                info.signerName = nz(sig.getName());
                info.reason = nz(sig.getReason());
                info.location = nz(sig.getLocation());
                info.contact = nz(sig.getContactInfo());
                Calendar c = sig.getSignDate();
                info.date = c == null ? "" : new SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.US).format(c.getTime());

                try {
                    // Validate the byte range first: a malformed range would otherwise be
                    // handed to the parser, which could try to allocate a huge buffer.
                    int[] br = sig.getByteRange();
                    if (br == null || br.length != 4 || br[0] < 0 || br[1] < 0 || br[2] < 0 || br[3] < 0
                            || (long) br[1] > src.length()
                            || (long) br[2] + (long) br[3] > src.length()) {
                        throw new IllegalArgumentException("Signature byte range is malformed");
                    }
                    byte[] signedContent;
                    byte[] contents;
                    try (InputStream is = new FileInputStream(src)) {
                        signedContent = sig.getSignedContent(is);
                    }
                    contents = sig.getContents();

                    CMSSignedData cms = parseCms(contents, signedContent);
                    SignerInformationStore store = cms.getSignerInfos();
                    boolean ok = false;
                    String verifyError = "";
                    for (SignerInformation si : store.getSigners()) {
                        for (Object o : cms.getCertificates().getMatches(si.getSID())) {
                            X509CertificateHolder holder = (X509CertificateHolder) o;
                            X509Certificate cert = new JcaX509CertificateConverter().getCertificate(holder);
                            // Record who signed even if the digest check later fails.
                            if (info.subject.isEmpty()) {
                                info.subject = cert.getSubjectX500Principal().getName();
                                info.issuer = cert.getIssuerX500Principal().getName();
                            }
                            try {
                                if (si.verify(new JcaSimpleSignerInfoVerifierBuilder().build(cert))) ok = true;
                            } catch (Exception ex) {
                                verifyError = ex.getClass().getSimpleName()
                                        + (ex.getMessage() == null ? "" : ": " + ex.getMessage());
                            }
                        }
                    }
                    info.valid = ok;
                    if (!ok) info.error = verifyError.isEmpty()
                            ? "Signature did not verify against the certificate" : verifyError;

                    // ByteRange is [start1, length1, start2, length2]: the signed ranges
                    // must start at 0 and reach the end of the file. The only gap is the
                    // /Contents placeholder that holds the signature itself.
                    info.coversWholeDocument =
                            br[0] == 0 && ((long) br[2] + (long) br[3]) == src.length();
                } catch (Exception e) {
                    info.valid = false;
                    info.error = e.getClass().getSimpleName() + (e.getMessage() == null ? "" : ": " + e.getMessage());
                }
                result.add(info);
            }
        }
        return result;
    }

    /** Parse the CMS blob, tolerating the zero padding PDF reserves for signatures. */
    private static CMSSignedData parseCms(byte[] contents, byte[] signedContent) throws Exception {
        try {
            return new CMSSignedData(new CMSProcessableByteArray(signedContent), contents);
        } catch (Exception first) {
            int len = contents.length;
            while (len > 1 && contents[len - 1] == 0) len--;
            if (len == contents.length) throw first;
            return new CMSSignedData(new CMSProcessableByteArray(signedContent),
                    Arrays.copyOf(contents, len));
        }
    }

    // ---------------------------------------------------------------------
    // Crypto helpers
    // ---------------------------------------------------------------------

    private static byte[] cmsSign(byte[] data, PrivateKey key, X509Certificate cert) throws IOException {
        try {
            CMSSignedDataGenerator gen = new CMSSignedDataGenerator();
            ContentSigner shaSigner = new JcaContentSignerBuilder("SHA256withRSA").build(key);
            gen.addSignerInfoGenerator(
                    new JcaSignerInfoGeneratorBuilder(new JcaDigestCalculatorProviderBuilder().build())
                            .build(shaSigner, cert));
            gen.addCertificates(new JcaCertStore(Collections.singletonList(cert)));
            CMSSignedData signed = gen.generate(new CMSProcessableByteArray(data), false);
            return signed.getEncoded();
        } catch (Exception e) {
            throw new IOException("Signing failed: " + e.getMessage(), e);
        }
    }

    private static KeyPair generateKeyPair() throws Exception {
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
        kpg.initialize(2048, new SecureRandom());
        return kpg.generateKeyPair();
    }

    private static X509Certificate selfSigned(KeyPair kp, String cn, String org) throws Exception {
        String commonName = (cn == null || cn.trim().isEmpty()) ? "KavoPDF signer" : cn.trim();
        String name = "CN=" + clean(commonName)
                + ((org == null || org.trim().isEmpty()) ? "" : ", O=" + clean(org.trim()));
        X500Principal principal = new X500Principal(name);

        long now = System.currentTimeMillis();
        Date from = new Date(now - 86400000L);
        Date to = new Date(now + 3650L * 86400000L);
        BigInteger serial = BigInteger.valueOf(now);

        JcaX509v3CertificateBuilder builder =
                new JcaX509v3CertificateBuilder(principal, serial, from, to, principal, kp.getPublic());
        builder.addExtension(Extension.basicConstraints, true, new BasicConstraints(false));
        builder.addExtension(Extension.keyUsage, true,
                new KeyUsage(KeyUsage.digitalSignature | KeyUsage.nonRepudiation));

        ContentSigner signer = new JcaContentSignerBuilder("SHA256withRSA").build(kp.getPrivate());
        X509CertificateHolder holder = builder.build(signer);
        return new JcaX509CertificateConverter().getCertificate(holder);
    }

    private static String clean(String s) {
        return s.replace(",", " ").replace("=", " ");
    }

    private static byte[] readAll(InputStream in) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int n;
        while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
        return out.toByteArray();
    }

    private static String nz(String s) { return s == null ? "" : s; }
}
