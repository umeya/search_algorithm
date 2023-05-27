### **このレポジトリ**
ここにあるものは、「ゲームで学ぶ　探索アルゴリズム　実践入門」（青木栄太、技術評論社）のコードをC++から[CODONコンパイラー](https://github.com/exaloop/codon)にとおるようにpythonで書き換えたものです。CODONについて理解が不十分で、CODON自体が開発中であったりしてコードがおかしなものになっているかもしれません。

### **実行環境について**
* windows11のWSL (Ubuntu 22.04.2 LTS)<br>wslttyが便利なので使っています。
* Python 3.10.6
* g++ 11.3.0 
* CODON ver0.6<br>下のシェルスクリプトをrun、buildするためにcodon_run.shとcodon_build.sh使っています。<br>
  `/home/user_name/.codon/bin`の部分はCODONインストール時に表示されるPATHです。

```sh:codon_run.sh
#!/bin/bash
export PATH=/home/user_name/.codon/bin:$PATH
codon run $1
```
```sh:codon_build.sh
#!/bin/bash
export PATH=/home/umeya/.codon/bin:$PATH
codon build  -release $1 -o $2
```
ソースコードをsrc、実行ファイルをbin、スクリーンショットをimgフォルダーに入れました。

### **各章にあるファイル**

### 第３章(ch3)「数字集め迷路」
#### src
* random_action.py <br>ランダムな移動をする探索
* greedy.py <br>貪欲法による探索
*  test_greedy_score.py <br>上の貪欲法による探索を１００万回実行したときの平均スコアを求める
*  beam_search.py <br>深さと幅を指定する探索。<br>
*  test_beam_search_score.py <br>上のbeam_searchによる探索を１００万回実行したときの平均スコアを求める
#### bin
* beam_search<br>beam_search.pyをCODONでコンパイル・ビルドした実行形式。オプションで迷路幅などを指定できる。（下のコマンドラインでの指定はデフォルト値）
```
./beam_search --MAZE_WIDTH=4 --MAZE_HEIGHT=3 --GAME_END_TURN=4 --PRINT_STATE=y --BEAM_WIDTH=2 --BEAM_DEPTH=4
```
* test_beam_search_score<br>上と同じ処理をした実行形式。test_beam_search_score.py、04a_TestBeamSearchScore.cppとの処理速度をするために作成した。04a_TestBeamSearchScore.cppは04_TestBeamSearchScore.cppの回数を100から100万回にかえたもので、比較はhyperfineで行い、その結果をプロンプトなど編集したものtest_beam_search_score.txtである。CODONでビルドしたほうがインタープリタのときよりも11倍速くなっているが、CPPのコンパイル・ビルドしたほうが２５０倍も速い！
```txt:test_beam_search_score.txt
foo@bar:/mnt/hoge/ch03$ hyperfine --min-runs 2  'python3 test_beam_search_score.py'  './test_beam_search_score'
Benchmark 1: python3 test_beam_search_score.py
  Time (mean ± σ):     128.335 s ±  8.127 s    [User: 128.322 s, System: 0.000 s]
  Range (min … max):   122.588 s … 134.082 s    2 runs

Benchmark 2: ./test_beam_search_score
  Time (mean ± σ):     10.926 s ±  0.228 s    [User: 7.887 s, System: 6.258 s]
  Range (min … max):   10.764 s … 11.087 s    2 runs

Summary
  './test_beam_search_score' ran
   11.75 ± 0.78 times faster than 'python3 test_beam_search_score.py'


foo@bar:/mnt/hoge/ch03$ hyperfine --min-runs 2  -i './test_beam_search_score' '04a_TestBeamSearchScore'
Benchmark 1: ./test_beam_search_score
  Time (mean ± σ):     10.916 s ±  0.013 s    [User: 7.860 s, System: 6.313 s]
  Range (min … max):   10.907 s … 10.926 s    2 runs

Benchmark 2: 04a_TestBeamSearchScore
  Time (mean ± σ):      42.8 ms ±   3.3 ms    [User: 3.1 ms, System: 2.8 ms]
  Range (min … max):    36.8 ms …  51.3 ms    65 runs

  Warning: Ignoring non-zero exit code.

Summary
  '04a_TestBeamSearchScore' ran
  255.18 ± 19.84 times faster than './test_beam_search_score'
```