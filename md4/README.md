# MD4

I'm picking MD4 as a starting point because most of the conceptual details are the same as that of MD5 (and also, RIPEMD, SHA), but the attacks are generally much more efficient, meaning I can implement them in Python without worrying about performance.

`md4.py` includes a basic implementation of the MD4 algorithm.

The basic ideas:

A message is padded and split into 512-bit (64 byte) blocks (often denoted M0, M1, ...Mn).

The state (4 x 32-bit words) is updated through successive application of the "compression function", i.e.

Sn+1 = md4_compress(Sn, Mn)

The initial state is an arbitrary hardcoded value ("nothing up my sleeve" numbers), and the final state is the hash output.

Internally, the compression function has 3 rounds, each of which consists of 16 steps, each reading a certain word of the message block as input.

The programmer-brain temptation is to think about these steps as imperative sequences of operations, but I find it much more useful to think about them as *functions*, that take the old state as input, along with part of the message, and return a new state.

# Attacks

### "An Attack on the Last Two Rounds of MD4" - Boer, Bosselaers, 1991

https://link.springer.com/chapter/10.1007/3-540-46766-1_14

> In this paper it is shown that if the three round MD4 algorithm is stripped of its first round, it is possible to find for a given (initial) input value two different messages hashing to the same output.
