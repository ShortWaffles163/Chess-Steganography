from time import time
from math import log2
from chess import pgn, Board
import io

def encode(input_source):
    start_time = time()
    
    # Handle both file paths and BytesIO objects
    if isinstance(input_source, io.BytesIO):
        data = input_source.read()
    else:
        with open(input_source, "rb") as f:
            data = f.read()
    
    # Convert to bitstream
    binary_string = ''.join(format(byte, '08b') for byte in data)
    bit_index = 0
    total_bits = len(binary_string)
    
    games = [] # List of lists of moves
    current_game_moves = []
    board = Board()
    
    while bit_index < total_bits:
        legal_moves = sorted(list(board.generate_legal_moves()), key=lambda m: m.uci())
        n = len(legal_moves)
        min_bits_per_move = 4   # The minimum number of bits needed per move
        # THRESHOLD CHECK: If < 16 moves, terminate game and start new one
        if n < 2**min_bits_per_move:
            if current_game_moves:
                games.append(current_game_moves)
            current_game_moves = []
            board = Board() # Reset board to start position
            continue
        
        # Calculate bits to encode (Adaptive)
        bits_available = int(log2(n))
        
        # Ensure we don't read past the end of the file
        chunk_size = min(bits_available, total_bits - bit_index)
        if chunk_size <= 0: break
            
        bit_chunk = binary_string[bit_index : bit_index + chunk_size]
        move_index = int(bit_chunk, 2)
        
        # Play the move
        if move_index < n:
            board.push(legal_moves[move_index])
            current_game_moves.append(legal_moves[move_index].uci())
            bit_index += chunk_size
        else:
            # Fallback if padding causes index out of range
            board.push(legal_moves[0])
            current_game_moves.append(legal_moves[0].uci())

    if current_game_moves:
        games.append(current_game_moves)
        
    print(f"Encoding complete in {round(time() - start_time, 3)}s. Games: {len(games)}")
    
    # Convert to PGN string
    pgn_string = ""
    for i, moves in enumerate(games):
        game = pgn.Game()
        node = game
        board = Board()
        for move_uci in moves:
            move = board.parse_uci(move_uci)
            node = node.add_variation(move)
            board.push(move)
        pgn_string += str(game) + "\n\n"
        
    return pgn_string
