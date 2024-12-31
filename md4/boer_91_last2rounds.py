import secrets
from .md4 import *

# this is the weakened version of MD4 that we'll be attacking
def md4_compress_last2(A, B, C, D, X):
	AA = A
	BB = B
	CC = C
	DD = D

	trace = []
	for i in range(16 * 2):
		#print(f"{i:>2}", hex(A), hex(B), hex(C), hex(D))
		#A, B, C, D = md4_step(A, B, C, D, X, 16 + i) # they call this an "elementary operation"
		A, B, C, D = MD4_STEP[16 + i](A, B, C, D, X)
		trace.append([X[Xk[16 + i]], A, B, C, D])
		#trace.append([X[Xk[16 + i]], [A, B, C, D][(-i)%4]]) # only record the word that changed

	A = (A + AA) & 0xffffffff
	B = (B + BB) & 0xffffffff
	C = (C + CC) & 0xffffffff
	D = (D + DD) & 0xffffffff

	return A, B, C, D, trace

N = 0x55555555

# nb: the defintion the paper uses for "odd" and "even" bits is counterintuitive!!!
def set_even_bits(n):
	return n | N

def clear_even_bits(n):
	return n & ~N

def collide():
	# step 1

	A0N_1 = clear_even_bits(secrets.randbits(32))
	A0N_2 = set_even_bits(A0N_1)
	B0N_1 = clear_even_bits(secrets.randbits(32))
	B0N_2 = set_even_bits(B0N_1)
	C0N_1 = clear_even_bits(secrets.randbits(32))
	C0N_2 = set_even_bits(C0N_1)
	D0N_1 = clear_even_bits(secrets.randbits(32))
	D0N_2 = set_even_bits(D0N_1)

	AN0_1 = set_even_bits(secrets.randbits(32))
	AN0_2 = clear_even_bits(AN0_1)
	BN0_1 = set_even_bits(secrets.randbits(32))
	BN0_2 = clear_even_bits(BN0_1)
	CN0_1 = set_even_bits(secrets.randbits(32))
	CN0_2 = clear_even_bits(CN0_1)
	DN0_1 = set_even_bits(secrets.randbits(32))
	DN0_2 = clear_even_bits(DN0_1)


	# step 2

	X1_1 = secrets.randbits(32)
	X2_1 = secrets.randbits(32)
	X5_1 = secrets.randbits(32) # not used until step 5
	X10_1 = secrets.randbits(32) # ditto
	X13_1 = secrets.randbits(32)
	X14_1 = secrets.randbits(32)

	# apply eqn 13
	A28 = rotl(AN0_1 + H(BN0_1, CN0_1, DN0_1) + X1_1 + E3, S31)
	X1_2 = (rotr(A28, S31) - (AN0_2 + H(BN0_2, CN0_2, DN0_2) + E3)) & 0xffffffff

	# apply eqn 5
	A12 = rotl(A0N_1 + G(B0N_1, C0N_1, D0N_1) + X2_1 + E2, S21)
	X2_2 = (rotr(A12, S21) - (A0N_2 + G(B0N_2, C0N_2, D0N_2) + E2)) & 0xffffffff

	# apply eqn 4
	B4 = (rotr(B0N_1, S24) - (G(C0N_1, D0N_1, A0N_1) + X13_1 + E2)) & 0xffffffff
	X13_2 = (rotr(B0N_2, S24) - (B4 + G(C0N_2, D0N_2, A0N_2) + E2)) & 0xffffffff

	# apply eqn 12
	B20 = (rotr(BN0_1, S34) - (H(CN0_1, DN0_1, AN0_1) + X14_1 + E3)) & 0xffffffff
	X14_2 = (rotr(BN0_2, S34) - (B20 + H(CN0_2, DN0_2, AN0_2) + E3)) & 0xffffffff


	# step 3
	# TODO...


def plot_traces(t1, t2):
	from matplotlib import pyplot as plt

	COLOURMAP = [
		[(  0, 0, 0), (  0, 255,   0)], # black, green
		[(255, 0, 0), (255, 255, 255)], # red, white
	]
	SPACER = (120, 120, 255)

	pixels = []
	for row1, row2 in zip(t1, t2):
		pxrow = []
		for word1, word2 in zip(row1, row2):
			for i in range(32):
				b1 = (word1 >> i) & 1
				b2 = (word2 >> i) & 1
				pxrow.append(COLOURMAP[b1][b2])
			pxrow.append(SPACER)
		pixels.append(pxrow)

	plt.imshow(pixels)
	plt.show()

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

	a1, b1, c1, d1, trace1 = md4_compress_last2(A0, B0, C0, D0, msg1)
	h1 = pack_state(a1, b1, c1, d1)
	a2, b2, c2, d2, trace2 = md4_compress_last2(A0, B0, C0, D0, msg2)
	h2 = pack_state(a2, b2, c2, d2)
	assert(h1 == h2)

	plot_traces(trace1, trace2)

	collide()
