from chess import *
import chess


class AmazonChessBoard(Board):
    """
    #see https://en.wikipedia.org/wiki/Maharajah_and_the_Sepoys
    """

    aliases = ["Maharajah and the Sepoys"]
    uci_variant = "shatranj"
    xboard_variant = "maharajah"
    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/8/4M3 w kq - 0 1"

    tbw_suffix = None
    tbz_suffix = None
    tbw_magic = None
    tbz_magic = None

    def __init__(self, fen: Optional[str] = starting_fen, chess960: bool = False) -> None:
        self.occupied = chess.BB_E1 | chess.BB_RANK_7 | chess.BB_RANK_8
        self.kings = chess.BB_E8
        self.queens = chess.BB_D8
        self.rooks = chess.BB_A8 | chess.BB_H8
        self.bishops = chess.BB_C8 | chess.BB_F8
        self.knights = chess.BB_B8 | chess.BB_G8
        self.pawns = chess.BB_RANK_7
        self.amazon = chess.BB_E1
        super().__init__(fen, chess960=chess960)

    def reset(self) -> None:
        self.set_fen(type(self).starting_fen)
        self.promoted = chess.BB_EMPTY
        self.amazon = chess.BB_E1

        self.occupied_co[chess.WHITE] = chess.BB_E1
        self.occupied_co[chess.BLACK] = chess.BB_RANK_7 | chess.BB_RANK_8

    def is_check(self) -> bool:
        """Tests if the current side to move is in check."""
        return bool(self.checkers_mask()) or self.is_attacked_by(chess.BLACK, self._amazon(chess.WHITE))

    def is_legal(self, move: chess.Move) -> bool:
        return not self.is_variant_end() and self.is_pseudo_legal(move) and not self.is_into_check(move)

    def is_into_check(self, move: Move) -> bool:

        if not self.turn: # Black have usual rule
            return super().is_into_check(move)

        amazon = self._amazon(self.turn)
        if amazon is None:
            return False

        # If already in check, look if it is an evasion.
        checkers = self.attackers_mask(not self.turn, amazon)
        if checkers and checkers & move.to_square:
            return True

        print(move.uci(),self.is_attacked_by(False, move.to_square))
        return self.is_attacked_by(not self.turn, move.to_square)

    def checkers_mask(self) -> Bitboard:
        king = self.king(self.turn)
        return chess.BB_EMPTY if king is None else self.attackers_mask(not self.turn, king)

    def piece_type_at(self, square: Square) -> Optional[PieceType]:
        """Gets the piece type at the given square."""
        mask = chess.BB_SQUARES[square]

        if not self.occupied & mask:
            return None  # Early return
        elif self.pawns & mask:
            return chess.PAWN
        elif self.knights & mask:
            return chess.KNIGHT
        elif self.bishops & mask:
            return chess.BISHOP
        elif self.rooks & mask:
            return chess.ROOK
        elif self.queens & mask:
            return chess.QUEEN
        elif self.amazon & mask:
            return chess.AMAZON
        else:
            return chess.KING

    def pieces_mask(self, piece_type: PieceType, color: Color) -> Bitboard:
        if piece_type == chess.PAWN:
            bb = self.pawns
        elif piece_type == chess.KNIGHT:
            bb = self.knights
        elif piece_type == chess.BISHOP:
            bb = self.bishops
        elif piece_type == chess.ROOK:
            bb = self.rooks
        elif piece_type == chess.QUEEN:
            bb = self.queens
        elif piece_type == chess.KING:
            bb = self.kings
        elif piece_type == chess.AMAZON:
            bb = self.amazon
        else:
            assert False, f"expected PieceType, got {piece_type!r}"

        return bb & self.occupied_co[color]

    def attacks_mask(self, square: Square) -> Bitboard:
        bb_square = chess.BB_SQUARES[square]

        if bb_square & self.pawns:
            color = bool(bb_square & self.occupied_co[chess.WHITE])
            return chess.BB_PAWN_ATTACKS[color][square]
        elif bb_square & self.knights:
            return chess.BB_KNIGHT_ATTACKS[square]
        elif bb_square & self.kings:
            return chess.BB_KING_ATTACKS[square]
        else:
            attacks = 0
            if bb_square & self.bishops or bb_square & self.queens or bb_square & self.amazon:
                attacks = chess.BB_DIAG_ATTACKS[square][chess.BB_DIAG_MASKS[square] & self.occupied]
            if bb_square & self.rooks or bb_square & self.queens or bb_square & self.amazon:
                attacks |= (chess.BB_RANK_ATTACKS[square][chess.BB_RANK_MASKS[square] & self.occupied] |
                            chess.BB_FILE_ATTACKS[square][chess.BB_FILE_MASKS[square] & self.occupied])
            if bb_square & self.amazon:
                attacks |= chess.BB_KNIGHT_ATTACKS[square]
            return attacks

    def attacks(self, square: Square) -> SquareSet:
        """
        Gets the set of attacked squares from the given square.

        There will be no attacks if the square is empty. Pinned pieces are
        still attacking other squares.

        Returns a :class:`set of squares <chess.SquareSet>`.
        """
        return chess.SquareSet(self.attacks_mask(square))

    def _attackers_mask(self, color: Color, square: Square, occupied: Bitboard) -> Bitboard:
        rank_pieces = chess.BB_RANK_MASKS[square] & occupied
        file_pieces = chess.BB_FILE_MASKS[square] & occupied
        diag_pieces = chess.BB_DIAG_MASKS[square] & occupied

        queens_and_rooks = self.queens | self.rooks
        queens_and_bishops = self.queens | self.bishops
        amazon = self.amazon

        attackers = (
                (chess.BB_KING_ATTACKS[square] & self.kings) |
                (chess.BB_KNIGHT_ATTACKS[square] & self.knights) |
                (chess.BB_KNIGHT_ATTACKS[square] & amazon) |
                (chess.BB_RANK_ATTACKS[square][rank_pieces] & queens_and_rooks) |
                (chess.BB_FILE_ATTACKS[square][file_pieces] & queens_and_rooks) |
                (chess.BB_DIAG_ATTACKS[square][diag_pieces] & queens_and_bishops) |
                (chess.BB_RANK_ATTACKS[square][rank_pieces] & amazon) |
                (chess.BB_FILE_ATTACKS[square][file_pieces] & amazon) |
                (chess.BB_DIAG_ATTACKS[square][diag_pieces] & amazon) |
                (chess.BB_PAWN_ATTACKS[not color][square] & self.pawns))

        return attackers & self.occupied_co[color]

    def attackers_mask(self, color: Color, square: Square) -> Bitboard:
        return self._attackers_mask(color, square, self.occupied)

    def is_attacked_by(self, color: Color, square: Square) -> bool:
        """
        Checks if the given side attacks the given square.

        Pinned pieces still count as attackers. Pawns that can be captured
        en passant are **not** considered attacked.
        """
        return bool(self.attackers_mask(color, square))

    def attackers(self, color: Color, square: Square) -> SquareSet:
        """
        Gets the set of attackers of the given color for the given square.

        Pinned pieces still count as attackers.

        Returns a :class:`set of squares <chess.SquareSet>`.
        """
        return SquareSet(self.attackers_mask(color, square))

    def pin_mask(self, color: Color, square: Square) -> Bitboard:
        king = self.king(color)
        if king is None:
            return chess.BB_ALL

        square_mask = chess.BB_SQUARES[square]

        for attacks, sliders in [(chess.BB_FILE_ATTACKS, self.rooks | self.queens | self.amazon),
                                 (chess.BB_RANK_ATTACKS, self.rooks | self.queens | self.amazon),
                                 (chess.BB_DIAG_ATTACKS, self.bishops | self.queens | self.amazon),
                                 ]:
            rays = attacks[king][0]
            if rays & square_mask:
                snipers = rays & sliders & self.occupied_co[not color]
                for sniper in scan_reversed(snipers):
                    if between(sniper, king) & (self.occupied | square_mask) == square_mask:
                        return ray(king, sniper)

                break

        return chess.BB_ALL

    def pin(self, color: Color, square: Square) -> SquareSet:
        """
        Detects an absolute pin (and its direction) of the given square to
        the king of the given color.

        >>> import chess
        >>>
        >>> board = chess.Board("rnb1k2r/ppp2ppp/5n2/3q4/1b1P4/2N5/PP3PPP/R1BQKBNR w KQkq - 3 7")
        >>> board.is_pinned(chess.WHITE, chess.C3)
        True
        >>> direction = board.pin(chess.WHITE, chess.C3)
        >>> direction
        SquareSet(0x0000_0001_0204_0810)
        >>> print(direction)
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        1 . . . . . . .
        . 1 . . . . . .
        . . 1 . . . . .
        . . . 1 . . . .
        . . . . 1 . . .

        Returns a :class:`set of squares <chess.SquareSet>` that mask the rank,
        file or diagonal of the pin. If there is no pin, then a mask of the
        entire board is returned.
        """
        return SquareSet(self.pin_mask(color, square))

    def is_pinned(self, color: Color, square: Square) -> bool:
        """
        Detects if the given square is pinned to the king of the given color.
        """
        return self.pin_mask(color, square) != chess.BB_ALL

    def _remove_piece_at(self, square: Square) -> Optional[PieceType]:
        piece_type = self.piece_type_at(square)
        mask = chess.BB_SQUARES[square]

        if piece_type == chess.PAWN:
            self.pawns ^= mask
        elif piece_type == chess.KNIGHT:
            self.knights ^= mask
        elif piece_type == chess.BISHOP:
            self.bishops ^= mask
        elif piece_type == chess.ROOK:
            self.rooks ^= mask
        elif piece_type == chess.QUEEN:
            self.queens ^= mask
        elif piece_type == chess.KING:
            self.kings ^= mask
        elif piece_type == chess.AMAZON:
            self.amazon ^= mask
        else:
            return None

        self.occupied ^= mask
        self.occupied_co[chess.WHITE] &= ~mask
        self.occupied_co[chess.BLACK] &= ~mask

        self.promoted &= ~mask

        return piece_type

    def remove_piece_at(self, square: Square) -> Optional[chess.Piece]:
        """
        Removes the piece from the given square. Returns the
        :class:`~chess.Piece` or ``None`` if the square was already empty.
        """
        color = bool(self.occupied_co[WHITE] & chess.BB_SQUARES[square])
        piece_type = self._remove_piece_at(square)
        return Piece(piece_type, color) if piece_type else None

    def _set_piece_at(self, square: Square, piece_type: PieceType, color: Color, promoted: bool = False) -> None:
        self._remove_piece_at(square)

        mask = chess.BB_SQUARES[square]

        if piece_type == chess.PAWN:
            self.pawns |= mask
        elif piece_type == chess.KNIGHT:
            self.knights |= mask
        elif piece_type == chess.BISHOP:
            self.bishops |= mask
        elif piece_type == chess.ROOK:
            self.rooks |= mask
        elif piece_type == chess.QUEEN:
            self.queens |= mask
        elif piece_type == chess.KING:
            self.kings |= mask
        elif piece_type == chess.AMAZON:
            self.amazon |= mask
        else:
            return

        self.occupied ^= mask
        self.occupied_co[color] ^= mask

        if promoted:
            self.promoted ^= mask

    def set_piece_at(self, square: Square, piece: Optional[Piece], promoted: bool = False) -> None:
        """
        Sets a piece at the given square.

        An existing piece is replaced. Setting *piece* to ``None`` is
        equivalent to :func:`~chess.Board.remove_piece_at()`.
        """
        if piece is None:
            self._remove_piece_at(square)
        else:
            self._set_piece_at(square, piece.piece_type, piece.color, promoted)

    def has_insufficient_material(self, color: chess.Color) -> bool:
        # The side with the king can always win by capturing the Horde.
        if color == chess.WHITE:
            return False
        return super().has_insufficient_material(chess.BLACK)

    def _amazon(self, color: Color) -> Optional[Square]:
        """
        Finds the amazon square of the given side. Returns ``None`` if there
        is no amazon found of that color.

        In variants with king promotions, only non-promoted kings are
        considered.
        """
        if color == chess.BLACK:
            return None
        amazon_mask = self.occupied_co[color]
        return chess.msb(amazon_mask)

    def status(self) -> chess.Status:
        status = super().status()
        if self.is_check():
            status |= chess.STATUS_OPPOSITE_CHECK | chess.STATUS_TOO_MANY_CHECKERS
        if self.turn == chess.BLACK and all(self.occupied_co[co] & self.kings & chess.BB_RANK_8 for co in chess.COLORS):
            status |= chess.STATUS_RACE_OVER
        if self.pawns:
            status |= chess.STATUS_RACE_MATERIAL
        for color in chess.COLORS:
            if chess.popcount(self.occupied_co[color] & self.knights) > 2:
                status |= chess.STATUS_RACE_MATERIAL
            if chess.popcount(self.occupied_co[color] & self.bishops) > 2:
                status |= chess.STATUS_RACE_MATERIAL
            if chess.popcount(self.occupied_co[color] & self.rooks) > 2:
                status |= chess.STATUS_RACE_MATERIAL
            if chess.popcount(self.occupied_co[color] & self.queens) > 1:
                status |= chess.STATUS_RACE_MATERIAL
        return status
