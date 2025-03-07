import unittest
import hedy
import sys
import io
from contextlib import contextmanager
import textwrap

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


class TestsLevel5(unittest.TestCase):
  level = 5
  
  def test_print_with_var(self):
    code = textwrap.dedent("""\
    naam is Hedy
    print 'ik heet' naam""")

    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    naam = 'Hedy'
    print('ik heet'+str(naam))""")

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)


  def test_transpile_ask(self):
    code = textwrap.dedent("""\
    antwoord is ask 'wat is je lievelingskleur?'""")

    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    antwoord = input('wat is je lievelingskleur?')""")

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

  # new tests for calculations
  def test_simple_calculation(self):
    code = "nummer is 4 + 5"
    result = hedy.transpile(code, self.level)

    expected = "nummer = int(4) + int(5)"
    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

  def test_addition_var(self):
    code = textwrap.dedent("""\
    var is 5
    print var + 5""")

    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    var = '5'
    print(str(int(var) + int(5)))""")

    self.assertEqual(expected, result.code)

  def test_simple_calculation_without_space(self):
    code = "nummer is 4+5"
    result = hedy.transpile(code, self.level)

    expected = "nummer = int(4) + int(5)"
    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

  def test_transpile_turtle_basic(self):
    code = textwrap.dedent("""\
    forward 50
    turn
    forward 100""")

    result = hedy.transpile(code, self.level)
    expected = textwrap.dedent("""\
    t.forward(50)
    time.sleep(0.1)
    t.right(90)
    t.forward(100)
    time.sleep(0.1)""")
    self.assertEqual(expected, result.code)
    self.assertEqual(True, result.has_turtle)


  def test_basic_calc(self):
    code = textwrap.dedent("""\
    print '5 keer 5 is ' 5 * 5""")

    expected = textwrap.dedent("""\
    print('5 keer 5 is '+str(int(5) * int(5)))""")

    result = hedy.transpile(code, self.level)

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

  def test_transpile_multiple_calcs(self):
    code = textwrap.dedent("""\
    print '5 keer 5 keer 5 is ' 5 * 5 * 5""")

    expected = textwrap.dedent("""\
    print('5 keer 5 keer 5 is '+str(int(5) * int(5) * int(5)))""")

    result = hedy.transpile(code, self.level)
    self.assertEqual(expected, result.code)

    output = run_code(result)
    self.assertEqual(output, '5 keer 5 keer 5 is 125')
    self.assertEqual(False, result.has_turtle)

  def test_allow_space_after_else_line(self):
    #this code has a space at the end of line 2
    code = textwrap.dedent("""\
    a is 2
    if a is 1 print a 
    else print 'nee'""")

    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    a = '2'
    if str(a) == str('1'):
      print(str(a))
    else:
      print('nee')""")

    self.assertEqual(expected, result.code)

  def test_transpile_turtle_with_ask(self):
    code = textwrap.dedent("""\
    afstand is ask 'hoe ver dan?'
    forward afstand""")
    result = hedy.transpile(code, self.level)
    expected = textwrap.dedent("""\
    afstand = input('hoe ver dan?')
    t.forward(afstand)
    time.sleep(0.1)""")
    self.assertEqual(expected, result.code)
    self.assertEqual(True, result.has_turtle)

  def test_calculation_and_printing(self):

    code = textwrap.dedent("""\
    nummer is 4 + 5
    print nummer""")

    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    nummer = int(4) + int(5)
    print(str(nummer))""")

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)
    self.assertEqual("9", run_code(result))

  def test_calculation_with_vars(self):
    code = textwrap.dedent("""\
    nummer is 5
    nummertwee is 6
    getal is nummer * nummertwee
    print getal""")

    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    nummer = '5'
    nummertwee = '6'
    getal = int(nummer) * int(nummertwee)
    print(str(getal))""")

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)
    self.assertEqual("30", run_code(result))

  def test_print_calculation_times_directly(self):
    code = textwrap.dedent("""\
    nummer is 5
    nummertwee is 6
    print nummer * nummertwee""")

    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    nummer = '5'
    nummertwee = '6'
    print(str(int(nummer) * int(nummertwee)))""")

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)
    self.assertEqual("30", run_code(result))

  def test_print_calculation_divide_directly(self):
    code = textwrap.dedent("""\
    nummer is 5
    nummertwee is 6
    print nummer / nummertwee""")

    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    nummer = '5'
    nummertwee = '6'
    print(str(int(nummer) // int(nummertwee)))""")

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)
    self.assertEqual("0", run_code(result))

  def test_issue_andras(self):
      code = textwrap.dedent("""\
      prijs is 0
      optiestoetje is ask 'zou u nog een toetje willen'
      if optiestoetje is ja toet is ask 'zou u een brownie of een ijsje willen' else print 'ok dan wordt het ' prijs ' euro'
      print toet
      if toet is ijsje prijs is prijs + 2
      print 'ok bedankt dan wordt het ' prijs ' euro'""")

      result = hedy.transpile(code, self.level)

      expected = textwrap.dedent("""\
        prijs = '0'
        optiestoetje = input('zou u nog een toetje willen')
        if str(optiestoetje) == str('ja'):
          toet = input('zou u een brownie of een ijsje willen')
        else:
          print('ok dan wordt het '+str(prijs)+' euro')
        print(str(toet))
        if str(toet) == str('ijsje'):
          prijs = int(prijs) + int(2)
        print('ok bedankt dan wordt het '+str(prijs)+' euro')""")

      self.assertEqual(expected, result.code)
      self.assertEqual(False, result.has_turtle)

  def test_print_and_else(self):
      code = textwrap.dedent("""\
      keuzes is 1, 2, 3, 4, 5, regenworm
      punten is 0
      worp is keuzes at random
      if worp is regenworm punten is punten + 5
      else punten is punten + worp
      print 'dat zijn dan ' punten""")

      result = hedy.transpile(code, self.level)

      expected = textwrap.dedent("""\
      keuzes = ['1', '2', '3', '4', '5', 'regenworm']
      punten = '0'
      worp=random.choice(keuzes)
      if str(worp) == str('regenworm'):
        punten = int(punten) + int(5)
      else:
        punten = int(punten) + int(worp)
      print('dat zijn dan '+str(punten))""")

      self.assertEqual(expected, result.code)
      self.assertEqual(False, result.has_turtle)


  def test_ifelse_should_go_before_assign(self):

    code = textwrap.dedent("""\
    kleur is geel
    if kleur is groen antwoord is ok else antwoord is stom
    print ans""")

    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    kleur = 'geel'
    if str(kleur) == str('groen'):
      antwoord = 'ok'
    else:
      antwoord = 'stom'
    print(str(ans))""")

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)
