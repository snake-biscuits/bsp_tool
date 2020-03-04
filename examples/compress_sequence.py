import itertools
import random

def all_indices(arr, value):
    next_start = 0
    indices = []
    while True:
        try:
            index = arr.index(value, next_start)
            next_start = index + 1
            indices.append(index)
        except:
            return(indices)

def compressed_len(*args):
    if len(args) == 2:
        return len(args[0] * 2) + len(args[1])
    elif len(args) == 3:
        return len(args[0] * 2) + len(args[1]) + len(args[2])
    else:
        raise NotImplemented('?')

def test_to(func, limit):
    chars = ['0', '1', '2', '3', '4', '5', '6', '7',
             '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    for x in range(limit):
        if (x + 1) % 256 == 0:
            print('\n{}'.format(x + 1))
        sequence = [random.randrange(-256, 256, 1) / 256 for y in range(x+1)]
        v, i = func(sequence)
        compressed_len = len(v) * 3 + len(i) / 2 # float32, uint16
        uncompressed_len = len(sequence) * 3
        if compressed_len > uncompressed_len:
            print('!', end='')
        elif compressed_len == uncompressed_len:
            print('@', end='')
        else:
            print(chars[round(compressed_len * 16 // uncompressed_len)], end='')

def vi_compress(sequence):
    """Compress into two lists:
Vertices - Original Data with no repeating values
Indices - Indices into the Vertex list used to rebuild original data
"""
    index = 0
    values = []
    indices = []
    for x in sequence:
        if x not in values:
            values.append(x)
            indices.append(index)
            index += 1
        else:
            indices.append(values.index(x))
    return values, indices

def sub_sequences(sequence, seq_len):
    for i in range(len(sequence) - seq_len + 1):
        yield sequence[i: i + seq_len]

# reduce repeats in indices
# for x in itertools.combinations(last_tier_subseqs):
#     x = [item for sublist in x for item in sublist]
#     if subsequence in x: #more complex test

def seq_compress(sequence): #not how that works
    """takes asequence and reduces all indices to repeating sub-sequences"""
    #reduce indices with sequences within and between sequences
    values, indices = vi_compress(sequence)
    sequences = []
    seq_tuples = []
    for seq_len in range(len(indices) // 2, 2, -1):
        for i, sub_seq in enumerate(sub_sequences(indices, seq_len)):
            start = i * seq_len
            if (start, seq_len) not in sequences:
                sequences.append((start , seq_len))
                seq_tuples.append((start , seq_len))
            else: #sequence occurs more than once
                #remove second occurence from
                pass
    return values, indices, sequences

def ref_unpack(references):
    for ref in references:
        print([x for x in range(ref[0], ref[0] + ref[1])])

def ref_compress(references):
    """>>> ref_compress([(2, 2), (5, 3), (0, 2)])
[(0, 4), (5, 3)]
Used for shortening calls to glDrawArrays and glDrawRangeElements"""
    r = []
    chain = False
    references = sorted(references, key=lambda x: x[0] + x[1])
    for ref, next_ref in zip(references, references[1:]):
        if next_ref[0] == ref[0] + ref[1]:
            if chain:
                r[-1] = r[-1][0], r[-1][1] + next_ref[1],
            else:
                r.append((ref[0], next_ref[1] + ref[1]))
                chain = True
        elif next_ref[0] < ref[0] + ref[1]:
            difference = next_ref[0] - ref[0] + next_ref[1]
            if chain:
                difference = ref[0] - r[-1][0] + ref[1]
                r[-1] = r[-1][0], difference,
            else:
                r.append((ref[0], difference))
                chain = True
        else:
            chain = False
            r.append(ref)
    return r

def ref_skipped(references):
    """returns indicies the references miss"""
    references = ref_compress(references)
    gaps = []
    for r, r2 in zip(references, references[1:]):
        gaps += range(r[0] + r[1], r2[0])
    return gaps


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "../")
    import bsp_tool # test what you're built for
    # test bsp face efficiency
    # bytesize of vertice + edges = surfedges + face references
    # vs length of raw vertices
##    test_to(vi_compress, 2048
    print(ref_compress([(0, 4), (2, 4), (2, 4), (4, 4), (4, 4), (8, 2)]))
