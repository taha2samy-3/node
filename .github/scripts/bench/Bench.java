import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.security.Signature;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.Mac;
import javax.crypto.SecretKey;

/**
 * JCE throughput of a Java image with whatever providers it has configured (BCFIPS in the FIPS
 * images, SunJCE in stock Temurin). Prints one JSON array. Written for Java 8 and later.
 */
public class Bench {
    interface Op { void run() throws Exception; }

    static final double SECONDS = Double.parseDouble(System.getProperty("bench.seconds", "1"));

    static double measure(Op op, int bytes) throws Exception {
        for (int i = 0; i < 200; i++) op.run(); // warm up the JIT
        long start = System.nanoTime();
        long end = start + (long) (SECONDS * 1e9);
        long count = 0;
        while (System.nanoTime() < end) {
            op.run();
            count++;
        }
        double elapsed = (System.nanoTime() - start) / 1e9;
        return bytes > 0 ? count * (double) bytes / elapsed / 1e6 : count / elapsed;
    }

    static String entry(String name, String metric, double value) {
        return String.format(java.util.Locale.ROOT, "{\"name\":\"%s\",\"metric\":\"%s\",\"value\":%.2f}", name, metric, value);
    }

    public static void main(String[] args) throws Exception {
        final byte[] data = new byte[16384];
        new SecureRandom().nextBytes(data);

        final MessageDigest sha256 = MessageDigest.getInstance("SHA-256");
        final MessageDigest sha512 = MessageDigest.getInstance("SHA-512");
        KeyGenerator aesGen = KeyGenerator.getInstance("AES");
        aesGen.init(256);
        final SecretKey aesKey = aesGen.generateKey();
        KeyGenerator hmacGen = KeyGenerator.getInstance("HmacSHA256");
        final Mac hmac = Mac.getInstance("HmacSHA256");
        hmac.init(hmacGen.generateKey());
        final Cipher gcm = Cipher.getInstance("AES/GCM/NoPadding");

        KeyPairGenerator ecGen = KeyPairGenerator.getInstance("EC");
        ecGen.initialize(256);
        final KeyPair ec = ecGen.generateKeyPair();
        KeyPairGenerator rsaGen = KeyPairGenerator.getInstance("RSA");
        rsaGen.initialize(2048);
        final KeyPair rsa = rsaGen.generateKeyPair();
        final Signature ecdsa = Signature.getInstance("SHA256withECDSA");
        final Signature rsaSha = Signature.getInstance("SHA256withRSA");

        ecdsa.initSign(ec.getPrivate());
        ecdsa.update(data);
        final byte[] ecSig = ecdsa.sign();
        rsaSha.initSign(rsa.getPrivate());
        rsaSha.update(data);
        final byte[] rsaSig = rsaSha.sign();

        StringBuilder out = new StringBuilder("[");
        out.append(entry("SHA-256", "MB/s", measure(() -> sha256.digest(data), data.length))).append(',');
        out.append(entry("SHA-512", "MB/s", measure(() -> sha512.digest(data), data.length))).append(',');
        out.append(entry("HMAC-SHA256", "MB/s", measure(() -> hmac.doFinal(data), data.length))).append(',');
        // The provider generates a fresh IV for every encryption (required for approved GCM)
        out.append(entry("AES-256-GCM encrypt", "MB/s", measure(() -> { gcm.init(Cipher.ENCRYPT_MODE, aesKey); gcm.doFinal(data); }, data.length))).append(',');
        out.append(entry("ECDSA P-256 sign", "ops/s", measure(() -> { ecdsa.initSign(ec.getPrivate()); ecdsa.update(data); ecdsa.sign(); }, 0))).append(',');
        out.append(entry("ECDSA P-256 verify", "ops/s", measure(() -> { ecdsa.initVerify(ec.getPublic()); ecdsa.update(data); ecdsa.verify(ecSig); }, 0))).append(',');
        out.append(entry("RSA-2048 sign", "ops/s", measure(() -> { rsaSha.initSign(rsa.getPrivate()); rsaSha.update(data); rsaSha.sign(); }, 0))).append(',');
        out.append(entry("RSA-2048 verify", "ops/s", measure(() -> { rsaSha.initVerify(rsa.getPublic()); rsaSha.update(data); rsaSha.verify(rsaSig); }, 0)));
        System.out.println(out.append(']'));
    }
}
