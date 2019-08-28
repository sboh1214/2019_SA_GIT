코드 수정을 마치고 develop 브랜치에 머지를 위한 pull request를 하기 전에 해야할 체크리스트입니다.


develop 브랜치
----
develop 브랜치에 머지를 요청하는 방법은 fork한 저장소에서 "Pull Request" 버튼을 누르고 나면 아래와 같이 맨 위에서 선택할 수 있습니다.

[[https://github.com/kakao/khaiii/blob/master/doc/img/pull-request-to-develop.png]]


테스트
----
빌드 방법에 따라 정상적으로 빌드 했다면, `build` 디렉토리 아래에서 다음과 같이 테스트를 실행할 수 있습니다.

```
$ test/khaiii
[==========] Running 13 tests from 4 test cases.
[----------] Global test environment set-up.
[----------] 1 test from ErrPatchTest
[ RUN      ] ErrPatchTest.apply
[       OK ] ErrPatchTest.apply (7 ms)
[----------] 1 test from ErrPatchTest (8 ms total)

[----------] 7 tests from KhaiiiApiTest
[ RUN      ] KhaiiiApiTest.version
[       OK ] KhaiiiApiTest.version (0 ms)
[ RUN      ] KhaiiiApiTest.open_close
[       OK ] KhaiiiApiTest.open_close (2 ms)
[ RUN      ] KhaiiiApiTest.analyze
[       OK ] KhaiiiApiTest.analyze (2 ms)
[ RUN      ] KhaiiiApiTest.free_results
[       OK ] KhaiiiApiTest.free_results (2 ms)
[ RUN      ] KhaiiiApiTest.last_error
[       OK ] KhaiiiApiTest.last_error (1 ms)
[ RUN      ] KhaiiiApiTest.restore_true
[       OK ] KhaiiiApiTest.restore_true (2 ms)
[ RUN      ] KhaiiiApiTest.restore_false
[       OK ] KhaiiiApiTest.restore_false (1 ms)
[----------] 7 tests from KhaiiiApiTest (10 ms total)

[----------] 3 tests from KhaiiiDevTest
[ RUN      ] KhaiiiDevTest.analyze_bfr_errorpatch
[       OK ] KhaiiiDevTest.analyze_bfr_errorpatch (1 ms)
[ RUN      ] KhaiiiDevTest.set_log_level
[       OK ] KhaiiiDevTest.set_log_level (1 ms)
[ RUN      ] KhaiiiDevTest.set_log_levels
[       OK ] KhaiiiDevTest.set_log_levels (1 ms)
[----------] 3 tests from KhaiiiDevTest (3 ms total)

[----------] 2 tests from PreanalTest
[ RUN      ] PreanalTest.apply_exact
[       OK ] PreanalTest.apply_exact (0 ms)
[ RUN      ] PreanalTest.apply_prefix
[       OK ] PreanalTest.apply_prefix (0 ms)
[----------] 2 tests from PreanalTest (0 ms total)

[----------] Global test environment tear-down
[==========] 13 tests from 4 test cases ran. (22 ms total)
[  PASSED  ] 13 tests.
```

만약 테스트가 깨진다면 pull request 전에 수정을 완료해 주시길 부탁드립니다.


PyLint
----
khaiii에 포함된 python 코드는 [PEP8](https://www.python.org/dev/peps/pep-0008/)을 따르고 있습니다. 그리고 이러한 코드 스타일을 체크하는 툴로 [pylint](https://www.pylint.org/)를 사용합니다. pylint를 실행하면 아래와 같은 메세지를 볼 수 있는데요,

```bash
$ pylint khaiii.py
No config file found, using default configuration
************* Module khaiii
R: 27, 0: Too few public methods (0/2) (too-few-public-methods)
R: 44, 0: Too few public methods (0/2) (too-few-public-methods)
R: 67, 0: Too few public methods (1/2) (too-few-public-methods)
W:110, 8: Unused variable 'morphs_str' (unused-variable)
R: 98, 0: Too few public methods (1/2) (too-few-public-methods)
W:160,12: Unused variable 'ext' (unused-variable)

------------------------------------------------------------------
Your code has been rated at 9.69/10 (previous run: 9.75/10, -0.06)
```

이러한 메세지들 중 'R' 레벨을 제외한 'E', 'W', 'C' 등의 메세지들은 나타나지 않도록 수정을 부탁드립니다.

다음과 같이 pip를 통해 git-pylint-commit-hook을 설치하고,

```
pip install git-pylint-commit-hook
```

커밋 전에 `git-pylint-commit-hook`이라고 명령을 하면 stage에 올라간 코드들에 대해 편리하게 pylint를 차례로 실행할 수 있습니다.

그리고 마지막으로, `.git/hooks/pre-commit` 파일에 `git-pylint-commit-hook`을 등록해 두면 커밋 명령 시 git-pylint-commit-hook을 자동으로 실행하고, 만약 pylint 에러가 존재할 경우 커밋이 중지됩니다. (권고 사항)


CppLint
----
khaiii에 포함된 C++ 코드는 [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)를 따르고 있습니다. 마찬가지로 [cpplint](https://github.com/cpplint/cpplint)라는 툴을 통해 스타일을 체크합니다. 아래와 같은 명령으로 cpplint를 실행하여 수정을 부탁드립니다.

```bash
$ cpplint --extensions=h,hh,hpp,c,cc,cpp --linelength=100 KhaiiiApi.hpp
KhaiiiApi.hpp:20:  Include the directory when naming .h files  [build/include_subdir] [4]
KhaiiiApi.hpp:70:  Lines should be <= 100 characters long  [whitespace/line_length] [2]
Done processing KhaiiiApi.hpp
Total errors found: 2
```

PEP8과 같이 khaiii에서는 라인의 최대 길이는 100으로 맞췄습니다. 그 외에는 Google C++ Style Guilde를 따르고 있습니다.

cpplint는 아래와 같이 pip를 통해 설치할 수 있습니다.

```
pip install cpplint
```

git-pylint-commit-hook 처럼 아래와 같은 스크립트를 `git-cpplit-commit-hook`이라는 이름으로 PATH 환경변수 경로에 두고 `.git/hooks/pre-commit` 파일에 등록해 두면 편리합니다. (권고 사항)

```bash
#!/usr/bin/env bash

cpplint_cmd="cpplint --extensions=c,cc,cpp,h,hh,hpp --linelength=100"

has_err=0
for i in $(git diff-index --cached --name-only HEAD | grep -e \\.c$ -e \\.cc$ -e \\.cpp$ -e \\.h$ -e \\.hh$ -e \\.hpp$); do
    if [ -f ${i} ]; then
        ${cpplint_cmd} ${i} || has_err=1
    fi
done
exit ${has_err}
```