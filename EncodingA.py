from time import time
from chess import pgn, Board
from util import to_binary_string, get_pgn_games

def encode(file_path):
    start_time = time()
    print("reading file...")
    
    # Handle file reading (supports BytesIO or file paths)
    if hasattr(file_path, 'read'):
        file_bytes = list(file_path.read())
    else:
        with open(file_path, "rb") as f:
            file_bytes = list(f.read())
            
    file_bits_count = len(file_bytes) * 8
    print("\nencoding file (Method B - Fixed 4-Bit)...")
    output_pgns: list[str] = []
    file_bit_index = 0
    chess_board = Board()
    
    FIXED_CHUNK_SIZE = 4
    
    while True:
        legal_moves = sorted(
            list(chess_board.generate_legal_moves()), 
            key=lambda m: m.uci()
        )
        
        # CRITICAL FIX: Start new game if < 16 legal moves
        if len(legal_moves) < (2 ** FIXED_CHUNK_SIZE):
            if chess_board.move_stack:  # Only save if moves were played
                pgn_board = pgn.Game()
                pgn_board.add_line(chess_board.move_stack)
                output_pgns.append(str(pgn_board))
            
            chess_board.reset()
            continue  # Re-process same bits on fresh board
        
        remaining_bits = file_bits_count - file_bit_index
        max_binary_length = min(FIXED_CHUNK_SIZE, remaining_bits)
        
        move_bits = {}
        for index, legal_move in enumerate(legal_moves):
            if index >= (2 ** FIXED_CHUNK_SIZE):
                break
            move_binary = to_binary_string(index, FIXED_CHUNK_SIZE)
            move_bits[legal_move.uci()] = move_binary
        
        closest_byte_index = file_bit_index // 8
        file_chunk_pool = "".join([
            to_binary_string(byte, 8)
            for byte in file_bytes[closest_byte_index : closest_byte_index + 2]
        ])
        next_file_chunk = file_chunk_pool[
            file_bit_index % 8 : file_bit_index % 8 + max_binary_length
        ]
        
        for move_uci, move_binary in move_bits.items():
            if move_binary == next_file_chunk:
                chess_board.push_uci(move_uci)
                break
        
        file_bit_index += max_binary_length
        
        eof_reached = file_bit_index >= file_bits_count
        if chess_board.is_game_over() or chess_board.can_claim_draw() or eof_reached:
            pgn_board = pgn.Game()
            pgn_board.add_line(chess_board.move_stack)
            output_pgns.append(str(pgn_board))
            chess_board.reset()
        
        if eof_reached:
            break
    
    print(
        f"\nsuccessfully converted file to pgn with "
        + f"{len(output_pgns)} game(s) "
        + f"({round(time() - start_time, 3)}s)."
    )
    return "\n\n".join(output_pgns)

# --- FIX: Main Guard Added ---
if __name__ == "__main__":
    msg = input("What's the message for Method B? ")
    while msg:
        with open('encoded_output_b.pgn', 'w') as pgn_file:
            print(encode(msg), file=pgn_file)
        msg = input("What's the next message? (Leave blank to quit): ")

