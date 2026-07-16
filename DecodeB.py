from time import time
from chess import pgn, Board
from util import to_binary_string, get_pgn_games

def decode(pgn_string: str, output_file_path: str):
    start_time = time()
    
    games: list[pgn.Game] = get_pgn_games(pgn_string)
    
    with open(output_file_path, "wb") as output_file:
        output_data = ""
        total_move_count = 0
        
        FIXED_CHUNK_SIZE = 4
        
        for game_index, game in enumerate(games):
            chess_board = Board()
            game_moves = list(game.mainline_moves())
            total_move_count += len(game_moves)
            
            for move_index, move in enumerate(game_moves):
                legal_move_ucis = [
                    legal_move.uci()
                    for legal_move in sorted(
                        list(chess_board.generate_legal_moves()), 
                        key=lambda m: m.uci()
                    )
                ]
                
                # Skip moves that carried no data (< 16 legal moves at time of encoding)
                if len(legal_move_ucis) < (2 ** FIXED_CHUNK_SIZE):
                    chess_board.push_uci(move.uci())
                    continue
                
                move_binary = bin(legal_move_ucis.index(move.uci()))[2:]
                
                # Pad to exactly 4 bits
                required_padding = max(0, FIXED_CHUNK_SIZE - len(move_binary))
                move_binary = ("0" * required_padding) + move_binary
                
                chess_board.push_uci(move.uci())
                output_data += move_binary
                
                # Flush complete bytes to file
                if len(output_data) >= 8:
                    full_bytes = len(output_data) // 8
                    output_file.write(
                        bytes([
                            int(output_data[i*8 : i*8+8], 2)
                            for i in range(full_bytes)
                        ])
                    )
                    output_data = output_data[full_bytes * 8:]
        
        # Write any remaining partial byte (should not happen with valid encoding)
        if output_data:
            output_data = output_data.ljust(8, '0')
            output_file.write(bytes([int(output_data, 2)]))
    
    print(
        f"\nsuccessfully decoded pgn with "
        + f"{len(games)} game(s), {total_move_count} total move(s)"
        + f" ({round(time() - start_time, 3)}s)."
    )
