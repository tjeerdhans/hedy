import unittest
import hedy
import sys
import io
import textwrap
from contextlib import contextmanager


@contextmanager
def captured_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def run_code(parse_result):
    code = "import random\n" + parse_result.code
    with captured_output() as (out, err):
        exec(code)
    return out.getvalue().strip()


class TestsLevel16(unittest.TestCase):
    maxDiff = None
    level = 16

    def test_print(self):
        result = hedy.transpile("print('ik heet')", self.level)
        expected = "print('ik heet')"
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_print_with_var(self):
        result = hedy.transpile("naam is Hedy\nprint('ik heet' naam)", self.level)
        expected = "naam = 'Hedy'\nprint('ik heet'+str(naam))"
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_print_with_calc_no_spaces(self):
        result = hedy.transpile("print('5 keer 5 is ' 5*5)", self.level)
        expected = "print('5 keer 5 is '+str(int(5) * int(5)))"
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_transpile_ask(self):
        result = hedy.transpile("antwoord is input('wat is je lievelingskleur?')", self.level)
        expected = "antwoord = input('wat is je lievelingskleur?')"
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_print_calculation_times_directly(self):
        code = textwrap.dedent("""\
    nummer is 5
    nummertwee is 6
    print(nummer * nummertwee)""")

        result = hedy.transpile(code, self.level)

        expected = textwrap.dedent("""\
    nummer = '5'
    nummertwee = '6'
    print(str(int(nummer) * int(nummertwee)))""")

        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

        self.assertEqual("30", run_code(result))


    def test_if_with_indent(self):
        code = textwrap.dedent("""\
naam is Hedy
if naam is Hedy:
    print('koekoek')""")
        expected = textwrap.dedent("""\
naam = 'Hedy'
if str(naam) == str('Hedy'):
  print('koekoek')""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_if_else(self):
        code = textwrap.dedent("""\
antwoord is input('Hoeveel is 10 plus 10?')
if antwoord is 20:
    print('Goedzo!')
    print('Het antwoord was inderdaad ' antwoord)
else:
    print('Foutje')
    print('Het antwoord moest zijn ' antwoord)""")

        expected = textwrap.dedent("""\
antwoord = input('Hoeveel is 10 plus 10?')
if str(antwoord) == str('20'):
  print('Goedzo!')
  print('Het antwoord was inderdaad '+str(antwoord))
else:
  print('Foutje')
  print('Het antwoord moest zijn '+str(antwoord))""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_print_random(self):
        code = textwrap.dedent("""\
    keuzes is ['steen', 'schaar', 'papier']
    computerkeuze is keuzes[random]
    print('computer koos ' computerkeuze)""")
        expected = textwrap.dedent("""\
    keuzes = ['steen', 'schaar', 'papier']
    computerkeuze=random.choice(keuzes)
    print('computer koos '+str(computerkeuze))""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_for_loop(self):
        code = textwrap.dedent("""\
    a is 2
    a is 3
    for a in range(2,4):
      a is a + 2
      b is b + 2""")
        expected = textwrap.dedent("""\
    a = '2'
    a = '3'
    step = 1 if int(2) < int(4) else -1
    for a in range(int(2), int(4) + step, step):
      a = int(a) + int(2)
      b = int(b) + int(2)""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_if__else(self):
        code = textwrap.dedent("""\
    a is 5
    if a is 1:
      x is 2
    else:
      x is 222""")
        expected = textwrap.dedent("""\
    a = '5'
    if str(a) == str('1'):
      x = '2'
    else:
      x = '222'""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_forloop(self):
        code = textwrap.dedent("""\
    for i in range(1, 10):
      print(i)
    print('wie niet weg is is gezien')""")
        expected = textwrap.dedent("""\
    step = 1 if int(1) < int(10) else -1
    for i in range(int(1), int(10) + step, step):
      print(str(i))
    print('wie niet weg is is gezien')""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_for_nesting(self):
        code = textwrap.dedent("""\
    for i in range(1, 3):
      for j in range(1,4):
        print('rondje: ' i ' tel: ' j)""")
        expected = textwrap.dedent("""\
    step = 1 if int(1) < int(3) else -1
    for i in range(int(1), int(3) + step, step):
      step = 1 if int(1) < int(4) else -1
      for j in range(int(1), int(4) + step, step):
        print('rondje: '+str(i)+' tel: '+str(j))""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_if_nesting(self):
        code = textwrap.dedent("""\
    kleur is blauw
    kleurtwee is geel
    if kleur is blauw:
      if kleurtwee is geel:
        print('Samen is dit groen!')""")
        expected = textwrap.dedent("""\
    kleur = 'blauw'
    kleurtwee = 'geel'
    if str(kleur) == str('blauw'):
      if str(kleurtwee) == str('geel'):
        print('Samen is dit groen!')""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_newprint(self):
        code = textwrap.dedent("""\
    leeftijd is input('Hoe oud ben jij?')
    print('Dus jij hebt zo veel verjaardagen gehad:')
    for i in range(0,leeftijd):
        print(i)""")
        expected = textwrap.dedent("""\
    leeftijd = input('Hoe oud ben jij?')
    print('Dus jij hebt zo veel verjaardagen gehad:')
    step = 1 if int(0) < int(leeftijd) else -1
    for i in range(int(0), int(leeftijd) + step, step):
      print(str(i))""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_list(self):
        code = textwrap.dedent("""\
    fruit is ['appel', 'banaan', 'kers']
    print(fruit)""")
        expected = textwrap.dedent("""\
    fruit = ['appel', 'banaan', 'kers']
    print(str(fruit))""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_random(self):
        code = textwrap.dedent("""\
    fruit is ['banaan', 'appel', 'kers']
    randomfruit is fruit[random]
    print(randomfruit)""")
        expected = textwrap.dedent("""\
    fruit = ['banaan', 'appel', 'kers']
    randomfruit=random.choice(fruit)
    print(str(randomfruit))""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_specific_access(self):
        code = textwrap.dedent("""\
    fruit is ['banaan', 'appel', 'kers']
    eerstefruit is fruit[1]
    print(eerstefruit)""")
        expected = textwrap.dedent("""\
    fruit = ['banaan', 'appel', 'kers']
    eerstefruit=fruit[1-1]
    print(str(eerstefruit))""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    # note that print(str(highscore)) will not print as it will compare 'score[i]' as str to a variable
    def test_everything_combined(self):
        code = textwrap.dedent("""\
    score is ['100', '300', '500']
    highscore is score[random]
    print('De highscore is: ' highscore)
    for i in range(1,3):
        scorenu is score[i]
        print('Score is nu ' scorenu)
        if highscore is score[i]:
            print(highscore)""")
        expected = textwrap.dedent("""\
    score = ['100', '300', '500']
    highscore=random.choice(score)
    print('De highscore is: '+str(highscore))
    step = 1 if int(1) < int(3) else -1
    for i in range(int(1), int(3) + step, step):
      scorenu=score[i-1]
      print('Score is nu '+str(scorenu))
      if str(highscore) == str('score[i]'):
        print(str(highscore))""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_if_under_else_in_for(self):
        code = textwrap.dedent("""\
    for i in range(0, 10):
      antwoord is input('Wat is 5*5')
      if antwoord is 24:
        print('Dat is fout!')
      else:
        print('Dat is goed!')
      if antwoord is 25:
        i is 10""")

        expected = textwrap.dedent("""\
    step = 1 if int(0) < int(10) else -1
    for i in range(int(0), int(10) + step, step):
      antwoord = input('Wat is 5*5')
      if str(antwoord) == str('24'):
        print('Dat is fout!')
      else:
        print('Dat is goed!')
      if str(antwoord) == str('25'):
        i = '10'""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_bool_true(self):
        code = textwrap.dedent("""\
    ja is True
    if ja is True:
        print('ja')""")
        expected = textwrap.dedent("""\
    ja = True
    if ja == True:
      print('ja')""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_bool_false(self):
        code = textwrap.dedent("""\
    ja is False
    if ja is False:
        print('ja')""")
        expected = textwrap.dedent("""\
    ja = False
    if ja == False:
      print('ja')""")
        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_bool_true2(self):
        code = textwrap.dedent("""\
    ja is true
    if ja is True:
        print('ja')""")
        expected = textwrap.dedent("""\
    ja = True
    if ja == True:
      print('ja')""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_bool_false2(self):
        code = textwrap.dedent("""\
    ja is false
    if ja is False:
        print('ja')""")
        expected = textwrap.dedent("""\
    ja = False
    if ja == False:
      print('ja')""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_bool_total(self):
        code = textwrap.dedent("""\
    jebenternog is False
    benjeernog is input('ben je er nog? ja of nee?')
    if benjeernog is ja:
        jebenternog is True
    if jebenternog is True:
        print('Hallo!')
    if jebenternog is False:
        print('Doei!')""")
        expected = textwrap.dedent("""\
    jebenternog = False
    benjeernog = input('ben je er nog? ja of nee?')
    if str(benjeernog) == str('ja'):
      jebenternog = True
    if jebenternog == True:
      print('Hallo!')
    if jebenternog == False:
      print('Doei!')""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_and(self):
        code = textwrap.dedent("""\
    if 5 is 5 and 4 is 4:
        print('hallo')""")
        expected = textwrap.dedent("""\
    if str('5') == str('5') and str('4') == str('4'):
      print('hallo')""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_or(self):
        code = textwrap.dedent("""\
    if 5 is 5 or 4 is 4:
        print('hallo')""")
        expected = textwrap.dedent("""\
    if str('5') == str('5') or str('4') == str('4'):
      print('hallo')""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_comment(self):
        code = textwrap.dedent("""\
    if 5 is 5 or 4 is 4:
        print('hallo')
        #comment""")
        expected = textwrap.dedent("""\
    if str('5') == str('5') or str('4') == str('4'):
      print('hallo')
      # ['comment']""")
        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_commentbegin(self):
        code = textwrap.dedent("""\
    # comment word
    if 5 is 5 or 4 is 4:
        print('hallo')
        """)
        expected = textwrap.dedent("""\
    # [' comment word']
    if str('5') == str('5') or str('4') == str('4'):
      print('hallo')""")
        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_commentresult(self):
        code = textwrap.dedent("""\
    # comment word
    if 5 is 5 or 4 is 4:
        print('hallo')
        """)
        expected = textwrap.dedent("""\
    # [' comment word']
    if str('5') == str('5') or str('4') == str('4'):
      print('hallo')""")
        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_smaller(self):
        code = textwrap.dedent("""\
    leeftijd is input('Hoe oud ben jij?')
    if leeftijd < 12:
        print('Dan ben je jonger dan ik!')""")
        expected = textwrap.dedent("""\
    leeftijd = input('Hoe oud ben jij?')
    if int(leeftijd) < int('12'):
      print('Dan ben je jonger dan ik!')""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_bigger(self):
        code = textwrap.dedent("""\
    leeftijd is input('Hoe oud ben jij?')
    if leeftijd > 12:
        print('Dan ben je ouder dan ik!')""")
        expected = textwrap.dedent("""\
    leeftijd = input('Hoe oud ben jij?')
    if int(leeftijd) > int('12'):
      print('Dan ben je ouder dan ik!')""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

    def test_big_and_small(self):
        code = textwrap.dedent("""\
    leeftijd is input('Hoe oud ben jij?')
    if leeftijd < 12:
        print('Dan ben je jonger dan ik!')
    elif leeftijd > 12:
        print('Dan ben je ouder dan ik!')""")
        expected = textwrap.dedent("""\
    leeftijd = input('Hoe oud ben jij?')
    if int(leeftijd) < int('12'):
      print('Dan ben je jonger dan ik!')
    elif int(leeftijd) > int('12'):
      print('Dan ben je ouder dan ik!')""")

        result = hedy.transpile(code, self.level)
        self.assertEqual(expected, result.code)
        self.assertEqual(False, result.has_turtle)

# programs with issues to see if we catch them properly
# (so this should fail, for now)
# at one point we want a real "Indent" error and a better error message
# for this!

# def test_level_7_no_indentation(self):
#   #test that we get a parse error here
#   code = textwrap.dedent("""\
#   antwoord is ask Hoeveel is 10 keer tien?
#   if antwoord is 100
#   print 'goed zo'
#   else
#   print 'bah slecht'""")
#
#   with self.assertRaises(Exception) as context:
#     result = hedy.transpile(code, 10)
#   self.assertEqual(str(context.exception), 'Parse')


