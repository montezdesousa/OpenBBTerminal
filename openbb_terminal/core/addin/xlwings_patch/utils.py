def chunk(sequence, chunksize):
    for i in range(0, len(sequence), chunksize):
        yield sequence[i : i + chunksize]