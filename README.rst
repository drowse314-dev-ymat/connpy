connpy -- search connpass on cli!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

connpassの検索をコマンドラインからやりたい変な人向け。

必要なもの
----------
- requests
- ねっと環境

検索
-----

オプションをフルに使うと::

    $ python connpy.py search Python web --search_or -n 4 --d 201302 -p

これで、Python + webで検索、ANDでなくORで、4つずつ表示、ページ化しない(4つ表示したらおわり)。

ブラウザで見る
--------------

検索で見つけたイベントの番号を使う::

    $ python connpy.py browse 999999

運が良ければ使っているブラウザで開きます。

その他
------

- setup.pyなどありません
- Web上には他の方が書かれたもっと使いやすいものが山ほどありますので…
