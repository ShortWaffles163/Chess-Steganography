from time import time
from chess import pgn, Board
import io

def get_pgn_games(pgn_string: str):
    games = []
    pgn_io = io.StringIO(pgn_string)
    while True:
        game = pgn.read_game(pgn_io)
        if game is None:
            break
        games.append(game)
    return games

def decode(pgn_string: str, output_file_path: str):
    start_time = time()
    
    games = get_pgn_games(pgn_string)
    
    if not games:
        print("Error: No valid games found in PGN string.")
        return b""

    with open(output_file_path, "wb") as output_file:
        output_data = ""
        total_move_count = 0
        FIXED_CHUNK_SIZE = 4
        
        for game in games:
            chess_board = Board()
            game_moves = list(game.mainline_moves())
            total_move_count += len(game_moves)
            
            for move in game_moves:
                legal_move_ucis = [
                    m.uci() for m in sorted(
                        list(chess_board.generate_legal_moves()), 
                        key=lambda x: x.uci()
                    )
                ]
                
                if len(legal_move_ucis) < (2 ** FIXED_CHUNK_SIZE):
                    chess_board.push_uci(move.uci())
                    continue
                
                try:
                    move_index_val = legal_move_ucis.index(move.uci())
                except ValueError:
                    chess_board.push_uci(move.uci())
                    continue 

                move_binary = bin(move_index_val)[2:]
                required_padding = max(0, FIXED_CHUNK_SIZE - len(move_binary))
                move_binary = ("0" * required_padding) + move_binary
                
                chess_board.push_uci(move.uci())
                output_data += move_binary
                
                if len(output_data) >= 8:
                    full_bytes = len(output_data) // 8
                    output_file.write(
                        bytes([int(output_data[i*8 : i*8+8], 2) for i in range(full_bytes)])
                    )
                    output_data = output_data[full_bytes * 8:]
        
        if output_data:
            output_data = output_data.ljust(8, '0')
            output_file.write(bytes([int(output_data, 2)]))
    
    print(f"\n[Decoder A] Successfully decoded: {len(games)} game(s), {total_move_count} moves ({round(time() - start_time, 3)}s).")

    with open(output_file_path, "rb") as f:
        result = f.read()
    
    # Print to Shell
    try:
        print(f"[Decoder A] Decoded Message: {result.decode('utf-8')}")
    except:
        print(f"[Decoder A] Decoded Bytes: {result}")
    
    return result

    
