Chess Steganography
Python implementation for hiding binary data inside chess games (PGN). Supports two encoding strategies evaluated in my science fair paper.
The Two Methods
Method A (Fixed-Rate): Encodes exactly 4 bits per half-move by selecting from the first 16 legal moves. Resets to a new game when <16 moves are available. Linear scaling, predictable throughput.
Method B (Adaptive Base-N): Dynamically encodes floor(log2(legal_moves)) bits per half-move. Uses all available entropy in openings, gracefully degrades in endgames. No forced resets.
Requirements
Python 3.8+
pip install python-chess
