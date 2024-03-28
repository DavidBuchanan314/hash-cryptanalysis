from .md4 import *

def md4_compress_last2(A, B, C, D, X):
	AA = A
	BB = B
	CC = C
	DD = D

	for i in range(16, 16 * 3):
		A, B, C, D = md4_step(A, B, C, D, X, i) # they call this an "elementary operation"

	A = (A + AA) & 0xffffffff
	B = (B + BB) & 0xffffffff
	C = (C + CC) & 0xffffffff
	D = (D + DD) & 0xffffffff

	return A, B, C, D

if __name__ == "__main__":
	# sanity check: verify their example collision

	msg1 = [x[0] for x in struct.iter_unpack(">I", bytes.fromhex("""
		72A3B049 213AE143 D954E8C9 50BD4CB5 25A3A0B3 C79B12BE 029B6AE9 091A6156
		75B5516B DA420FD6 0A6854EB 758F514D 9EA01345 0F796EAC DB54B645 4089373B
	"""))]

	msg2 = [x[0] for x in struct.iter_unpack(">I", bytes.fromhex("""
		72A3B049 CBE58BED 2EAA3E1F 50BD4CB5 25A3A0B3 7245BD68 57F0C03F 091A6156
		75B5516B 2F97652B B512FF96 758F514D 9EA01345 64CEC401 85FF60F0 4089373B
	"""))]

	a1, b1, c1, d1 = md4_compress_last2(A0, B0, C0, D0, msg1)
	print(hex(a1), hex(b1), hex(c1), hex(d1))

	a2, b2, c2, d2 = md4_compress_last2(A0, B0, C0, D0, msg2)
	print(hex(a2), hex(b2), hex(c2), hex(d2))

	# oh no it doesn't work, lol
	# not sure the best way to troubleshoot this...
