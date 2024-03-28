"""
https://www.rfc-editor.org/rfc/rfc1320

There's like, 3 different implementations of md4 here, it remains to be seen which formulation(s)
will actually be useful
"""
import struct

def msg_pad(msg: bytes) -> bytes:
	return msg + b"\x80" + bytes((-len(msg) - 9) % 64) + (len(msg) * 8).to_bytes(8, "little")

A0 = 0x67452301
B0 = 0xefcdab89
C0 = 0x98badcfe
D0 = 0x10325476

S11 =  3
S12 =  7
S13 = 11
S14 = 19

S21 =  3
S22 =  5
S23 =  9
S24 = 13

S31 =  3
S32 =  9
S33 = 11
S34 = 15

S = (
	[S11, S12, S13, S14] * 4 +
	[S21, S22, S23, S24] * 4 +
	[S31, S32, S33, S34] * 4
)

Xk1 = [
	 0,  1,  2,  3,
	 4,  5,  6,  7,
	 8,  9, 10, 11,
	12, 13, 14, 15,
]
Xk2 = [
	 0,  4,  8, 12,
	 1,  5,  9, 13,
	 2,  6, 10, 14,
	 3,  7, 11, 15,
]
Xk3 = [
	 0,  4,  8, 12,
	 2, 10,  6, 14,
	 1,  9,  5, 13,
	 3, 11,  7, 15,
]
Xk = Xk1 + Xk2 + Xk3

def F(X,Y,Z):
	return (X & Y) | (~X & Z)

def G(X,Y,Z):
	return (X & Y) | (X & Z) | (Y & Z)

def H(X,Y,Z):
	return X ^ Y ^ Z

def rotl(x, n):
	return ((x << n) & 0xffffffff) | ((x & 0xffffffff) >> (32 - n))

def FF(a, b, c, d, x, s):
	return rotl(a + F(b, c, d) + x, s)

def GG(a, b, c, d, x, s):
	return rotl(a + G(b, c, d) + x + 0x5A827999, s)

def HH(a, b, c, d, x, s):
	return rotl(a + H(b, c, d) + x + 0x6ED9EBA1, s)

sfn = [FF] * 16 + [GG] * 16 + [HH] * 16

shuf = [
	lambda a, b, c, d, x, s, fn: (fn(a, b, c, d, x, s), b, c, d),
	lambda a, b, c, d, x, s, fn: (a, b, c, fn(d, a, b, c, x, s)),
	lambda a, b, c, d, x, s, fn: (a, b, fn(c, d, a, b, x, s), d),
	lambda a, b, c, d, x, s, fn: (a, fn(b, c, d, a, x, s), c, d),
] * 4 * 3

def md4_step(a, b, c, d, X, n):
	return shuf[n](a, b, c, d, X[Xk[n]], S[n], sfn[n])

MD4_STEP = [
	# round 1
	lambda a, b, c, d, X: (FF(a, b, c, d, X[ 0], S11), b, c, d),
	lambda a, b, c, d, X: (a, b, c, FF(d, a, b, c, X[ 1], S12)),
	lambda a, b, c, d, X: (a, b, FF(c, d, a, b, X[ 2], S13), d),
	lambda a, b, c, d, X: (a, FF(b, c, d, a, X[ 3], S14), c, d),

	lambda a, b, c, d, X: (FF(a, b, c, d, X[ 4], S11), b, c, d),
	lambda a, b, c, d, X: (a, b, c, FF(d, a, b, c, X[ 5], S12)),
	lambda a, b, c, d, X: (a, b, FF(c, d, a, b, X[ 6], S13), d),
	lambda a, b, c, d, X: (a, FF(b, c, d, a, X[ 7], S14), c, d),

	lambda a, b, c, d, X: (FF(a, b, c, d, X[ 8], S11), b, c, d),
	lambda a, b, c, d, X: (a, b, c, FF(d, a, b, c, X[ 9], S12)),
	lambda a, b, c, d, X: (a, b, FF(c, d, a, b, X[10], S13), d),
	lambda a, b, c, d, X: (a, FF(b, c, d, a, X[11], S14), c, d),

	lambda a, b, c, d, X: (FF(a, b, c, d, X[12], S11), b, c, d),
	lambda a, b, c, d, X: (a, b, c, FF(d, a, b, c, X[13], S12)),
	lambda a, b, c, d, X: (a, b, FF(c, d, a, b, X[14], S13), d),
	lambda a, b, c, d, X: (a, FF(b, c, d, a, X[15], S14), c, d),

	# round 2
	lambda a, b, c, d, X: (GG(a, b, c, d, X[ 0], S21), b, c, d),
	lambda a, b, c, d, X: (a, b, c, GG(d, a, b, c, X[ 4], S22)),
	lambda a, b, c, d, X: (a, b, GG(c, d, a, b, X[ 8], S23), d),
	lambda a, b, c, d, X: (a, GG(b, c, d, a, X[12], S24), c, d),

	lambda a, b, c, d, X: (GG(a, b, c, d, X[ 1], S21), b, c, d),
	lambda a, b, c, d, X: (a, b, c, GG(d, a, b, c, X[ 5], S22)),
	lambda a, b, c, d, X: (a, b, GG(c, d, a, b, X[ 9], S23), d),
	lambda a, b, c, d, X: (a, GG(b, c, d, a, X[13], S24), c, d),

	lambda a, b, c, d, X: (GG(a, b, c, d, X[ 2], S21), b, c, d),
	lambda a, b, c, d, X: (a, b, c, GG(d, a, b, c, X[ 6], S22)),
	lambda a, b, c, d, X: (a, b, GG(c, d, a, b, X[10], S23), d),
	lambda a, b, c, d, X: (a, GG(b, c, d, a, X[14], S24), c, d),

	lambda a, b, c, d, X: (GG(a, b, c, d, X[ 3], S21), b, c, d),
	lambda a, b, c, d, X: (a, b, c, GG(d, a, b, c, X[ 7], S22)),
	lambda a, b, c, d, X: (a, b, GG(c, d, a, b, X[11], S23), d),
	lambda a, b, c, d, X: (a, GG(b, c, d, a, X[15], S24), c, d),

	# round 3
	lambda a, b, c, d, X: (HH(a, b, c, d, X[ 0], S31), b, c, d),
	lambda a, b, c, d, X: (a, b, c, HH(d, a, b, c, X[ 4], S32)),
	lambda a, b, c, d, X: (a, b, HH(c, d, a, b, X[ 8], S33), d),
	lambda a, b, c, d, X: (a, HH(b, c, d, a, X[12], S34), c, d),

	lambda a, b, c, d, X: (HH(a, b, c, d, X[ 2], S31), b, c, d),
	lambda a, b, c, d, X: (a, b, c, HH(d, a, b, c, X[10], S32)),
	lambda a, b, c, d, X: (a, b, HH(c, d, a, b, X[ 6], S33), d),
	lambda a, b, c, d, X: (a, HH(b, c, d, a, X[14], S34), c, d),

	lambda a, b, c, d, X: (HH(a, b, c, d, X[ 1], S31), b, c, d),
	lambda a, b, c, d, X: (a, b, c, HH(d, a, b, c, X[ 9], S32)),
	lambda a, b, c, d, X: (a, b, HH(c, d, a, b, X[ 5], S33), d),
	lambda a, b, c, d, X: (a, HH(b, c, d, a, X[13], S34), c, d),

	lambda a, b, c, d, X: (HH(a, b, c, d, X[ 3], S31), b, c, d),
	lambda a, b, c, d, X: (a, b, c, HH(d, a, b, c, X[11], S32)),
	lambda a, b, c, d, X: (a, b, HH(c, d, a, b, X[ 7], S33), d),
	lambda a, b, c, d, X: (a, HH(b, c, d, a, X[15], S34), c, d),
]

def md4_block(A, B, C, D, X):
	# save original values
	AA = A
	BB = B
	CC = C
	DD = D

	# round 1 (I wonder if I should keep these unrolled or turn them into a loop?)
	A = FF(A, B, C, D, X[ 0],  3)
	D = FF(D, A, B, C, X[ 1],  7)
	C = FF(C, D, A, B, X[ 2], 11)
	B = FF(B, C, D, A, X[ 3], 19)

	A = FF(A, B, C, D, X[ 4],  3)
	D = FF(D, A, B, C, X[ 5],  7)
	C = FF(C, D, A, B, X[ 6], 11)
	B = FF(B, C, D, A, X[ 7], 19)

	A = FF(A, B, C, D, X[ 8],  3)
	D = FF(D, A, B, C, X[ 9],  7)
	C = FF(C, D, A, B, X[10], 11)
	B = FF(B, C, D, A, X[11], 19)

	A = FF(A, B, C, D, X[12],  3)
	D = FF(D, A, B, C, X[13],  7)
	C = FF(C, D, A, B, X[14], 11)
	B = FF(B, C, D, A, X[15], 19)

	# round 2
	A = GG(A, B, C, D, X[ 0],  3)
	D = GG(D, A, B, C, X[ 4],  5)
	C = GG(C, D, A, B, X[ 8],  9)
	B = GG(B, C, D, A, X[12], 13)

	A = GG(A, B, C, D, X[ 1],  3)
	D = GG(D, A, B, C, X[ 5],  5)
	C = GG(C, D, A, B, X[ 9],  9)
	B = GG(B, C, D, A, X[13], 13)

	A = GG(A, B, C, D, X[ 2],  3)
	D = GG(D, A, B, C, X[ 6],  5)
	C = GG(C, D, A, B, X[10],  9)
	B = GG(B, C, D, A, X[14], 13)

	A = GG(A, B, C, D, X[ 3],  3)
	D = GG(D, A, B, C, X[ 7],  5)
	C = GG(C, D, A, B, X[11],  9)
	B = GG(B, C, D, A, X[15], 13)

	# round 3
	A = HH(A, B, C, D, X[ 0],  3)
	D = HH(D, A, B, C, X[ 4],  9)
	C = HH(C, D, A, B, X[ 8], 11)
	B = HH(B, C, D, A, X[12], 15)

	A = HH(A, B, C, D, X[ 2],  3)
	D = HH(D, A, B, C, X[10],  9)
	C = HH(C, D, A, B, X[ 6], 11)
	B = HH(B, C, D, A, X[14], 15)

	A = HH(A, B, C, D, X[ 1],  3)
	D = HH(D, A, B, C, X[ 9],  9)
	C = HH(C, D, A, B, X[ 5], 11)
	B = HH(B, C, D, A, X[13], 15)

	A = HH(A, B, C, D, X[ 3],  3)
	D = HH(D, A, B, C, X[11],  9)
	C = HH(C, D, A, B, X[ 7], 11)
	B = HH(B, C, D, A, X[15], 15)

	# add back the original values
	A = (A + AA) & 0xffffffff
	B = (B + BB) & 0xffffffff
	C = (C + CC) & 0xffffffff
	D = (D + DD) & 0xffffffff

	return A, B, C, D


def md4_block_stepped(A, B, C, D, X):
	# save original values
	AA = A
	BB = B
	CC = C
	DD = D

	for stepfn in MD4_STEP:
		A, B, C, D = stepfn(A, B, C, D, X)

	# add back the original values
	A = (A + AA) & 0xffffffff
	B = (B + BB) & 0xffffffff
	C = (C + CC) & 0xffffffff
	D = (D + DD) & 0xffffffff

	return A, B, C, D

def md4_block_stepped2(A, B, C, D, X):
	# save original values
	AA = A
	BB = B
	CC = C
	DD = D

	for i in range(16 * 3):
		A, B, C, D = md4_step(A, B, C, D, X, i)

	# add back the original values
	A = (A + AA) & 0xffffffff
	B = (B + BB) & 0xffffffff
	C = (C + CC) & 0xffffffff
	D = (D + DD) & 0xffffffff

	return A, B, C, D

def iter_blocks(padded: bytes):
	return struct.iter_unpack("<16I", padded)

def pack_state(a, b, c, d):
	return struct.pack("<IIII", a, b, c, d)

def md4(msg, blockfn=md4_block_stepped2):
	padded = msg_pad(msg)
	A, B, C, D = A0, B0, C0, D0

	for M in struct.iter_unpack("<16I", padded):
		A, B, C, D = blockfn(A, B, C, D, M)

	h = struct.pack("<IIII", A, B, C, D)
	return h


if __name__ == "__main__":
	h = md4(b"abc", blockfn=md4_block)
	assert(h.hex() == "a448017aaf21d8525fc10ae87aa6729d")
	h = md4(b"abc", blockfn=md4_block_stepped)
	assert(h.hex() == "a448017aaf21d8525fc10ae87aa6729d")
	h = md4(b"abc", blockfn=md4_block_stepped)
	assert(h.hex() == "a448017aaf21d8525fc10ae87aa6729d")
	print(h.hex())
