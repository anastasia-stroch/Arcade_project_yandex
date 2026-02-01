import sqlite3
from datetime import datetime


class GameDatabase:
    def __init__(self, db_name="game_scores.db"):
        self.db_name = db_name
        self.setup_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def setup_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_stats (
                id INTEGER PRIMARY KEY,
                best_level INTEGER DEFAULT 1,
                total_coins INTEGER DEFAULT 0,
                total_score INTEGER DEFAULT 0,
                games_count INTEGER DEFAULT 0,
                last_played TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS best_scores (
                id INTEGER PRIMARY KEY,
                player_name TEXT DEFAULT 'Игрок',
                score INTEGER,
                level INTEGER,
                coins INTEGER,
                date TEXT
            )
        ''')

        cursor.execute('SELECT COUNT(*) FROM player_stats')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO player_stats (best_level, total_coins, total_score, games_count, last_played)
                VALUES (1, 0, 0, 0, ?)
            ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))

        conn.commit()
        conn.close()

    def save_game_result(self, level, coins, score):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT best_level, total_coins, total_score, games_count FROM player_stats WHERE id=1')
            row = cursor.fetchone()

            if row:
                old_best, old_coins, old_score, old_games = row

                new_best = max(old_best, level)
                new_coins = old_coins + coins
                new_score = old_score + score
                new_games = old_games + 1

                cursor.execute('''
                    UPDATE player_stats 
                    SET best_level=?, total_coins=?, total_score=?, games_count=?, last_played=?
                    WHERE id=1
                ''', (
                    new_best,
                    new_coins,
                    new_score,
                    new_games,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

            conn.commit()
            conn.close()
        except:
            ...

    def add_score(self, player_name, score, level, coins):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO best_scores (player_name, score, level, coins, date)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                player_name,
                score,
                level,
                coins,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            cursor.execute('''
                DELETE FROM best_scores 
                WHERE id NOT IN (
                    SELECT id FROM best_scores 
                    ORDER BY score DESC 
                    LIMIT 10
                )
            ''')

            conn.commit()
            conn.close()
        except:
            ...

    def get_top_scores(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                'SELECT player_name, score, level, coins, date FROM best_scores ORDER BY score DESC LIMIT 10')

            scores = []
            for row in cursor.fetchall():
                scores.append({
                    'name': row[0],
                    'score': row[1],
                    'level': row[2],
                    'coins': row[3],
                    'date': row[4]
                })

            conn.close()
            return scores
        except:
            return []

    def get_my_stats(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM player_stats WHERE id=1')
            row = cursor.fetchone()

            conn.close()

            if row:
                return {
                    'best_level': row[1],
                    'total_coins': row[2],
                    'total_score': row[3],
                    'games_count': row[4],
                    'last_played': row[5]
                }
            return None
        except:
            return None

    def clear_all(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM best_scores')
            cursor.execute('UPDATE player_stats SET best_level=1, total_coins=0, total_score=0, games_count=0')

            conn.commit()
            conn.close()
        except:
            ...


db = GameDatabase()