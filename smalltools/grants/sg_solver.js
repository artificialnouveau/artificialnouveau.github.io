// SiteGround captcha PoW solver.
// Replicates the logic from the JS challenge: take sgchallenge string, append
// little-endian-encoded nonce bytes, pad to multiple of 4 bytes with zeros,
// compute SHA1, and find the lowest nonce such that the first word interpreted
// as big-endian has top `complexity` bits zero.
//
// Looking at the original JS: it does Int32Array(buffer).map(p) where p is a
// byteswap (turning little-endian Int32 read into big-endian). So effectively
// the SHA1 is computed over the byte-swapped Int32 view, equivalent to the
// raw bytes treated as a big-endian-on-the-wire stream.
//
// Then checks: l.words[0] >>> (32 - complexity) == 0
// So we want the first 4 bytes of the SHA1 (as big-endian Int32) to have the
// top `complexity` bits zero.

const crypto = require('crypto');

function encodeNonce(c) {
    // var e = 1; if (c > 0xFFFFFF) e=4; else if (c > 0xFFFF) e=3; else if (c > 0xFF) e=2;
    // BIG-ENDIAN encoding of the integer (most significant byte first)
    let e = 1;
    if (c > 0xFFFFFF) e = 4;
    else if (c > 0xFFFF) e = 3;
    else if (c > 0xFF) e = 2;
    const r = Buffer.alloc(e);
    let v = c;
    for (let n = e - 1; n >= 0; n--) {
        r[n] = v & 0xFF;
        v = v >>> 8;
    }
    return r;
}

function solve(challenge, complexity, startFrom) {
    const challengeBytes = Buffer.from(challenge, 'utf8');
    let c = startFrom;
    const limit = 5e7; // 50M hashes max
    for (let i = 0; i < limit; i++, c++) {
        const nonceBytes = encodeNonce(c);
        const r = challengeBytes.length + nonceBytes.length;
        const pad = r % 4 === 0 ? 0 : 4 - (r % 4);
        const buf = Buffer.alloc(r + pad);
        challengeBytes.copy(buf, 0);
        nonceBytes.copy(buf, challengeBytes.length);
        const h = crypto.createHash('sha1').update(buf).digest();
        // Check top `complexity` bits of first 4 bytes
        // Words[0] >>> (32 - complexity) == 0
        // i.e. firstWord (big-endian) < 2^(32 - complexity)
        const firstWord = (h[0] << 24) | (h[1] << 16) | (h[2] << 8) | h[3];
        // Use unsigned shift
        if (((firstWord >>> 0) >>> (32 - complexity)) === 0) {
            // Return base64 of the challenge+nonce bytes (without padding)
            const out = Buffer.alloc(r);
            challengeBytes.copy(out, 0);
            nonceBytes.copy(out, challengeBytes.length);
            return out.toString('base64');
        }
    }
    return null;
}

const challenge = process.argv[2];
const parts = challenge.split(':');
const complexity = parseInt(parts[0], 10);
const startFrom = Math.floor(Math.random() * 5e6);
console.error(`Solving challenge complexity=${complexity} from=${startFrom}`);
const t0 = Date.now();
const sol = solve(challenge, complexity, startFrom);
const t1 = Date.now();
if (sol === null) {
    console.error('No solution found');
    process.exit(1);
}
console.error(`Solved in ${t1 - t0}ms`);
console.log(sol); // base64
console.log(t1 - t0); // elapsed ms
