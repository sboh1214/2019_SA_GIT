학습 코퍼스
----

khaiii는 세종 코퍼스 형식의 코퍼스를 학습에 사용합니다. 세종 코퍼스는 아래와 같은 포맷을 가집니다.

```
<text>
<group>
<text>
<body>
<source>
<date>
BTAA0001-00000001       1993/06/08      1993/SN + //SP + 06/SN + //SP + 08/SN
</date>
<page>
BTAA0001-00000002       19      19/SN
</page>
</source>
<head>
BTAA0001-00000003       엠마누엘        엠마누엘/NNP
BTAA0001-00000004       웅가로  웅가로/NNP
BTAA0001-00000005       /       //SP
BTAA0001-00000006       의상서  의상/NNG + 서/JKB
BTAA0001-00000007       실내    실내/NNG
BTAA0001-00000008       장식품으로…     장식품/NNG + 으로/JKB + …/SE
BTAA0001-00000009       디자인  디자인/NNG
BTAA0001-00000010       세계    세계/NNG
BTAA0001-00000011       넓혀    넓히/VV + 어/EC
</head>
<p>
BTAA0001-00000012       프랑스의        프랑스/NNP + 의/JKG
BTAA0001-00000013       세계적인        세계/NNG + 적/XSN + 이/VCP + ㄴ/ETM
BTAA0001-00000014       의상    의상/NNG
BTAA0001-00000015       디자이너        디자이너/NNG
BTAA0001-00000016       엠마누엘        엠마누엘/NNP
BTAA0001-00000017       웅가로가        웅가로/NNP + 가/JKS
BTAA0001-00000018       실내    실내/NNG
BTAA0001-00000019       장식용  장식/NNG + 용/XSN
BTAA0001-00000020       직물    직물/NNG
BTAA0001-00000021       디자이너로      디자이너/NNG + 로/JKB
BTAA0001-00000022       나섰다. 나서/VV + 었/EP + 다/EF + ./SF
</p>
```

이러한 형식 중에서 헤더나 기타 메타 정보들은 제외하고 `<p>`와 `</p>`, `<head>`와 `</head>` 혹은 `<l>`과 `</l>`로 둘러싸인 부분만을 문장으로 인식하여 학습에 사용합니다.


실행 환경
----

학습에 필요한 스크립트는 `train` 디렉토리 아래에 있으며 `train` 디렉토리에서 `./map_char_to_tag.py`와 같이 실행한다고 가정하고 기술하겠습니다.

실행 스크립트들이 필요로하는 python 모듈은 `src/main/python` 아래에 있습니다. 따라서 다음과 같이 `PYTHONPATH` 환경을 export 해야 합니다.

```bash
export PYTHONPATH=/path/to/khaiii/src/main/python
```

학습을 위해서는 아래 패키지가 필요합니다.
* tensorboardX
* tqdm

아래와 같이 pip 명령을 통해 설치하시면 됩니다.

```bash
pip install tensorboardX tqdm
```

PyTorch의 경우 현재 0.4.1 버전에서 학습이 제대로 이뤄지고 있으며, 1.0 버전에서는 정상적으로 학습되지 않습니다. (이 부분은 추후에 수정하도록 하겠습니다.) 따라서 virtualenv 등의 환경 관리 툴을 통해 반드시 0.4.1 버전의 PyTorch를 설치하여 학습을 진행하시기 바랍니다. PyTorch의 설치는 [PyTorch 홈페이지](https://pytorch.org)를 참고하시기 바랍니다.


음절 단위 정렬
----

아래와 같은 명령을 통해 어절의 원문과 형태소 분석 결과를 음절 단위로 정렬합니다.

```bash
./map_char_to_tag.py -c corpus --output corpus.txt --restore-dic restore.dic
```

`-c corpus` 옵션은 코퍼스 파일이 있는 디렉토리입니다. 세종 코퍼스는 원래 UTF-16 인코딩으로 배포되고 있습니다. 본 스크립트를 수행하기 위해서는 UTF-8 형식으로 변환해 주어야 합니다.

`--output corpus.txt` 옵션은 정렬을 수행한 결과 파일입니다. 정상적으로 수행되었다면 아래와 같은 형식의 파일이 생성됩니다.

```
엠마누엘	I-NNP I-NNP I-NNP I-NNP
웅가로	I-NNP I-NNP I-NNP
/	I-SP
의상서	I-NNG I-NNG I-JKB
실내	I-NNG I-NNG
장식품으로…	I-NNG I-NNG I-NNG I-JKB I-JKB I-SE
디자인	I-NNG I-NNG I-NNG
세계	I-NNG I-NNG
넓혀	I-VV I-VV:I-EC:0

프랑스의	I-NNP I-NNP I-NNP I-JKG
세계적인	I-NNG I-NNG I-XSN I-VCP:I-ETM:0
의상	I-NNG I-NNG
디자이너	I-NNG I-NNG I-NNG I-NNG
엠마누엘	I-NNP I-NNP I-NNP I-NNP
웅가로가	I-NNP I-NNP I-NNP I-JKS
실내	I-NNG I-NNG
장식용	I-NNG I-NNG I-XSN
직물	I-NNG I-NNG
디자이너로	I-NNG I-NNG I-NNG I-NNG I-JKB
나섰다.	I-VV I-VV:I-EP:0 I-EF I-SF
```

`--restore-dic restore.dic` 옵션은 원형복원 사전 파일입니다. 정상적으로 수행되었다면 아래와 같은 형식의 파일이 생성됩니다.

```
혀/I-VV:I-EC:0	히/I-VV 어/I-EC
혀/I-VV:I-EC:1	히/I-VV 여/I-EC
혀/I-VV:I-EC:2	허/I-VV 어/I-EC
혀/I-VV:I-EC:3	하/I-VV 여/I-EC
혀/I-VV:I-EC:4	혀/I-VV 어/I-EC
혀/I-VV:I-EC:5	치/I-VV 어/I-EC
혀/I-VV:I-EC:6	히/I-VV 아/I-EC
인/I-VCP:I-ETM:0	이/I-VCP ㄴ/I-ETM
인/I-VCP:I-ETM:1	이/I-VCP 은/I-ETM
섰/I-VV:I-EP:0	서/I-VV 었/I-EP
섰/I-VV:I-EP:1	시/I-VV 었/I-EP
섰/I-VV:I-EP:2	스/I-VV 었/I-EP
```

생성된 `restore.dic` 파일은 이후 학습 과정에서 필요로 하므로 `rsc/src` 아래에 복사해 줘야합니다.


학습 코퍼스 분할
----

아래 명령을 통해 `map_char_to_tag.py`에 의해 생성된 학습 코퍼스를 dev / test / train 세개로 분할합니다.

```bash
./split_corpus.py --input corpus.txt -o corpus
```

`--input corpus.txt` 옵션은 이전 `map_char_to_tag.py` 스크립트의 결과인 분할할 코퍼스입니다.

`-o corpus` 옵션은 출력할 파일의 prefix입니다. 가령 `corpus`라고 했다면 `corpus.dev`, `corpus.test`, `corpus.train` 세개의 파일로 나눠집니다.


vocab 생성
----

학습에 사용할 코퍼스를 이용하여 입, 출력 vocab을 생성하는 명령은 아래와 같습니다.

```bash
./make_vocab.py --input corpus.train
```

`--input corpus.train` 옵션을 통해 앞서 분할한 코퍼스의 train 부분입니다.

`--rsc-src` 옵션을 별도로 지정하지 않으면, 현재 디렉터리로부터 `../rsc/src` 디렉터리를 사용하게 되며, 이 디렉터리에 `vocab.in` 및 `vocab.out` 파일이 생성됩니다.

`vocab.in` 파일은 아래와 같이 음절과 빈도가 명시되어 있는 파일입니다.

```
齒  25
齡  8
龍  300
龕  8
龜  16
가  499305
각  58237
간  77133
갇  478
갈  15383
```

`vocab.out` 파일은 빈도가 없이 출력 태그만 명시되어 있는 파일입니다.

```
I-XSN
I-XSV
I-ZN
I-ZV
I-ZZ
B-EP:I-EC:0
B-EP:I-EF:0
B-EP:I-ETM:0
B-JKB:I-JKG:0
B-JKB:I-JX:0
```


모델 학습
----

코퍼스와 vocab 파일이 준비되면 다음과 같은 명령으로 학습을 시작합니다.

```bash
./train.py -i corpus
```

`-i corpus` 옵션은 `corpus.train`, `corpus.dev`, `corpus.test` 파일의 공통 prefix 부분을 명시합니다.

만약 large 모델을 학습하는 경우 `--embed-dim 150` 옵션을 추가해 주면 됩니다.

학습이 정상적으로 진행되면 아래와 같은 화면이 출력됩니다.

```
INFO:root:vocab.in: 5109 entries, 512 cutoff
INFO:root:vocab.out: 500 entries, 0 cutoff
INFO:root:restore.dic: 4303 entries
munjong.dev: 100%|█████████████████████████████████████████| 64444/64444 [00:01<00:00, 43958.83it/s]
INFO:root:munjong.dev: 5000 sentences
munjong.test: 100%|████████████████████████████████████████| 64589/64589 [00:01<00:00, 39999.19it/s]
INFO:root:munjong.test: 5000 sentences
munjong.train: 100%|█████████████████████████████████| 10763939/10763939 [04:51<00:00, 36971.95it/s]
INFO:root:munjong.train: 844614 sentences
INFO:root:config: {'batch_size': 500,
 'best_epoch': 0,
 'context_len': 7,
 'cutoff': 2,
 'debug': False,
 'embed_dim': 30,
 'epoch': 0,
 'gpu_num': 5,
 'hidden_dim': 310,
 'in_pfx': 'corpus',
 'learning_rate': 0.001,
 'logdir': './logdir5',
 'lr_decay': 0.9,
 'model_id': 'corpus.cut2.win3.sdo0.0.emb30.lr0.001.lrd0.9.bs500',
 'out_dir': './logdir/corpus.cut2.win3.sdo0.0.emb30.lr0.001.lrd0.9.bs500',
 'patience': 10,
 'rsc_src': '../rsc/src',
 'spc_dropout': 0.0,
 'window': 3}
INFO:root:{{{{ training begin: 02/01 13:49:10 {{{{
EPOCH[0]: 100%|████████████████████████████████████████████| 844614/844614 [51:17<00:00, 274.42it/s]
INFO:root:[Los trn]  [Los dev]  [Acc chr]  [Acc wrd]  [F-score]           [LR]
INFO:root:   0.2512     0.1866     0.9448     0.8876     0.9269 BEST      0.00100000
EPOCH[1]: 100%|████████████████████████████████████████████| 844614/844614 [49:59<00:00, 281.55it/s]
INFO:root:[Los trn]  [Los dev]  [Acc chr]  [Acc wrd]  [F-score]           [LR]
INFO:root:   0.1654     0.1675     0.9496     0.8968     0.9333 BEST      0.00100000
EPOCH[2]: 100%|████████████████████████████████████████████| 844614/844614 [50:39<00:00, 277.84it/s]
INFO:root:[Los trn]  [Los dev]  [Acc chr]  [Acc wrd]  [F-score]           [LR]
INFO:root:   0.1530     0.1638     0.9515     0.8989     0.9348 BEST      0.00100000

...

EPOCH[90]: 100%|███████████████████████████████████████████| 844614/844614 [49:24<00:00, 284.94it/s]
INFO:root:[Los trn]  [Los dev]  [Acc chr]  [Acc wrd]  [F-score]           [LR]
INFO:root:   0.1058     0.1237     0.9651     0.9259     0.9524 < 0.9525  0.00000247
INFO:root:}}}} training end: 02/04 15:25:15, elapsed: 73:36:05, epoch: 90 }}}}
INFO:root:==== test loss: 0.1241, char acc: 0.9651, word acc: 0.9258, f-score: 0.9526 ====
```

학습 진행에 따른 그래프는 기본 로그 경로인 `./logdir` 아래에서 TensorBoard를 이용해 확인하실 수 있습니다.

학습은 더이상 dev 코퍼스의 성능이 높아지지 않을 때까지 진행하고 자동으로 종료됩니다. 전체 코퍼스를 사용할 경우 NVIDIA P40 GPU 1개를 기준으로 약 3일 정도의 시간이 필요합니다.

학습 결과는 `./logdir/corpus.cut2.win3.sdo0.0.emb30.lr0.001.lrd0.9.bs500`와 같은 디렉토리 아래에 다음과 같은 파일들이 생성됩니다.
* config.json
* events.out.tfevents.0000000000.hostname
* log.tsv
* model.state
* optim.state

이 중 `config.json` 및 `model.state` 파일은 이후 리소스 빌드 과정에서 필요하므로 삭제하지 않도록 주의합니다.

학습이 완료된 모델을 이용해 간단히 형태소 분석을 수행하는 스크립트는 아래와 같이 실행할 수 있습니다.

```bash
$ ./tag.py -m ./logdir/corpus.cut2.win3.sdo0.0.emb30.lr0.001.lrd0.9.bs500
INFO:root:vocab.in: 5109 entries, 512 cutoff
INFO:root:vocab.out: 500 entries, 0 cutoff
INFO:root:restore.dic: 4303 entries
안녕? 세상.
안녕?	안녕/IC + ?/SF
세상.	세상/NNG + ./SF
```

학습 스크립트의 옵션에 관한 설명은 아래와 같습니다.

옵션             | 설명                                    | 기본값
----------------|----------------------------------------|----- 
-i, --in-pfx    | 학습 코퍼스 경로의 공통 prefix 부분           |
--rsc-src       | 리소스 소스 디렉터리                        | ../rsc/src
--logdir        | 로그를 저장할 디렉토리                       | ./logdir
--window        | 음절 좌/우 문맥 크기                        | 3
--spc-dropout   | 공백 dropout 비율                         | 0.0
--cutoff        | 입력 vocab 엔트리의 최소 빈도                 | 2
--embed-dim     | 임베딩 차원                                | 30
--learning-rate | 초기 learning rate                       | 0.001
--lr-decay      | learning rate 감소 비율                   | 0.9
--batch-size    | 배치 크기                                 | 500
--patience      | 최고 성능 갱신이 없어도 더 학습을 진행할 epoch 수 | 10
--gpu-num       | 사용할 GPU 번호                            | 0
--debug         | 디버그 정보 표시                            |


pickle 파일 생성
----

위 학습 결과물 중 `model.state` 파일은 PyTorch 버전에 의존성을 갖습니다. 이러한 의존성을 제거하기 위해 학습 후 pickle 파일을 생성하여 이후 리소스 빌드 과정에서 PyTorch 패키지가 없어도 빌드할 수 있도록 해주는 작업이 필요합니다.

다음과 같은 명령을 이용해 pickle 파일을 생성합니다.

```bash
./pickle_model.py -i ./logdir/corpus.cut2.win3.sdo0.0.emb30.lr0.001.lrd0.9.bs500
```

`-i ./logdir/corpus.cut2.win3.sdo0.0.emb30.lr0.001.lrd0.9.bs500`는 학습 결과 디렉토리를 지정하는 옵션입니다.

아래는 이 스크립트를 통해 변환되어 저장되는 base 모델 파일에 대한 목록입니다.

./logdir/corpus.cut2.win3.sdo0.0.emb30.lr0.001.lrd0.9.bs500 | ../rsc/src
------------------------------------------------------------|-----------
config.json                                                 | base.config.json
model.state                                                 | base.model.pickle
