#!/usr/bin/env python3
"""
ポケモン風ゲーム - メインエントリーポイント
"""

import sys
import os

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.game_engine import main

if __name__ == "__main__":
    main()