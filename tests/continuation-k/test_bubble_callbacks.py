"""Existing R03 UI callbacks, composed with native initialization/registration.

Read-only inputs; UIKit, Objective-C dispatch, allocation and callback delivery
are explicit providers. This does not install methods into a real process.
"""
from pathlib import Path
import os, sys, json, struct, hashlib

HERE = Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS', str(HERE.parents[1] / 'results/generated/continuation-k'))
sys.path.insert(0, str(HERE.parent / 'continuation-j'))
from test_overlay_return_menu import *

UI_STATE = 0x1013780
CONTROL_A = 0x200c0000
CONTROL_B = 0x200c0100
BUTTON = 0x200c1000
PAN = 0x200c2000
UI_VALUE = 0x200c3000


class Bubble(ReturnModel):
 def __init__(self, main=True, button_ok=True, pan_mode='ready'):
  super().__init__(P, True, True, [])
  self.e.write(UI_STATE, bytes(0x300))
  self.ui_main = main
  self.button_ok = button_ok
  self.pan_mode = pan_mode
  self.classes = {}
  self.methods = {}
  self.ui_events = []
  self.center = (0., 0.)
  self.bounds = (0., 0., 320., 240.)
  self.translation = (800., -800.)
  self.gesture_state = 2
  self.parent = 0
  self.target = None
  self.gesture_target = None
  self.e.write(CONTROL_A, bytes(256))
  self.e.write(CONTROL_B, bytes(256))

 def add_method(self, e):
  selector = e.cs(e.get(1))
  if selector in ('v58InstallBubble:', 'v58TapBubble:', 'v58PanBubble:'):
   self.methods[selector] = e.get(2)
  return super().add_method(e)

 def lookup_class(self, e):
  name = e.cs(e.get(0))
  super().lookup_class(e)
  self.classes[name] = e.get(0)

 def prepare(self, control=CONTROL_A, factory=False):
  # No manually populated UI selector/class cache: native registration fills it.
  assert self.e.q(UI_STATE + 0x100) == 0
  self.fp(0., 0., 320., 240.)
  if factory:
   result = self.nested(0x68401c, [(0, OVERLAYCLASS), (2, control),
                                 (3, 0), (4, 0), (5, 0)])
   assert result == SELF
  else:
   hit, result = self.initialize(control, stop=STOP, windows=(0, 0, 0))
   assert hit == STOP and result == SELF
  self.verify_return_hook('r03')
  assert self.methods == {'v58InstallBubble:': 0x1016820,
                         'v58TapBubble:': 0x1016a80,
                         'v58PanBubble:': 0x1016b60}
  assert self.e.q(UI_STATE + 0x100) != 0
  assert self.e.q(UI_STATE) == 0 and self.parent == 0

 def invoke(self, selector, argument=0, receiver=SELF):
  # Manual delivery, not an assertion about the real main queue or UI routing.
  assert selector in self.methods
  sel = next(a for s, a in self.selector_cache() if s == selector)
  return self.nested(self.methods[selector], [(0, receiver), (1, sel), (2, argument)])

 def selector_cache(self):
  return [(self.e.cs(self.e.q(UI_STATE + 0x100 + 8*i)),
           self.e.q(UI_STATE + 0x100 + 8*i)) for i in range(34)]

 def message(self, e):
  receiver, selector, arg = e.get(0), e.cs(e.get(1)), e.get(2)
  if not receiver:
   e.set(0, 0)
   return
  if receiver == self.classes.get('NSThread') and selector == 'isMainThread':
   e.set(0, self.ui_main)
   self.ui_events.append(dict(selector=selector, returned=self.ui_main))
   return
  if selector == 'buttonWithType:':
   assert receiver == self.classes['UIButton'] and arg == 0
   e.set(0, BUTTON if self.button_ok else 0)
   self.ui_events.append(dict(selector=selector, returned=hex(e.get(0))))
   return
  if receiver == BUTTON:
   if selector == 'setFrame:':
    rect = [self.fp_get(i) for i in range(4)]
    self.center = (rect[0] + rect[2]/2, rect[1] + rect[3]/2)
   elif selector == 'center':
    self.fp(*self.center)
   elif selector == 'setCenter:':
    self.center = (self.fp_get(), self.fp_get(1))
   elif selector == 'addTarget:action:forControlEvents:':
    self.target = (arg, e.cs(e.get(3)), e.get(4))
    assert self.target == (SELF, 'v58TapBubble:', 0x40)
   elif selector == 'addGestureRecognizer:':
    assert arg == PAN
   elif selector in ('layer', 'titleLabel'):
    e.set(0, UI_VALUE)
   elif selector == 'removeFromSuperview':
    self.parent = 0
   elif selector not in ('setTitle:forState:', 'setTitleColor:forState:',
                         'setBackgroundColor:'):
    raise AssertionError(('Unexpected button selector', selector))
   self.ui_events.append(dict(selector=selector, center=list(self.center)))
   return
  if receiver == SELF and selector in ('bounds', 'addSubview:', 'bringSubviewToFront:'):
   if selector == 'bounds':
    self.fp(*self.bounds)
   else:
    assert arg == BUTTON
    if selector == 'addSubview:':
     self.parent = receiver
   self.ui_events.append(dict(selector=selector))
   return
  if receiver == self.classes.get('UIPanGestureRecognizer') and selector == 'alloc':
   e.set(0, 0 if self.pan_mode == 'alloc_nil' else PAN)
   self.ui_events.append(dict(selector='pan alloc', returned=hex(e.get(0))))
   return
  if receiver == PAN:
   if selector == 'initWithTarget:action:':
    self.gesture_target = (arg, e.cs(e.get(3)))
    assert self.gesture_target == (SELF, 'v58PanBubble:')
    e.set(0, 0 if self.pan_mode == 'init_nil' else PAN)
   elif selector in ('setMaximumNumberOfTouches:', 'setCancelsTouchesInView:'):
    assert arg == 1
   elif selector == 'state':
    e.set(0, self.gesture_state)
   elif selector == 'translationInView:':
    assert arg == SELF
    self.fp(*self.translation)
   elif selector == 'setTranslation:inView:':
    assert arg == SELF
    self.translation = (self.fp_get(), self.fp_get(1))
   else:
    raise AssertionError(('Unexpected pan selector', selector))
   self.ui_events.append(dict(selector=selector))
   return
  if receiver == self.classes.get('NSString') and selector == 'stringWithUTF8String:':
   e.set(0, UI_VALUE)
   return
  if receiver == self.classes.get('UIColor') and selector in (
      'whiteColor', 'colorWithRed:green:blue:alpha:'):
   e.set(0, UI_VALUE)
   return
  if receiver == self.classes.get('UIFont') and selector == 'boldSystemFontOfSize:':
   e.set(0, UI_VALUE)
   return
  if receiver == UI_VALUE and selector in ('setCornerRadius:', 'setFont:'):
   return
  return super().message(e)

 def snapshot(self):
  return dict(button=hex(self.e.q(UI_STATE)), owner=hex(self.e.q(UI_STATE+8)),
              flags=int.from_bytes(self.e.u.mem_read(UI_STATE+0x20, 4), 'little'),
              center=list(self.center), parent=hex(self.parent),
              target=list(self.target) if self.target else None,
              gesture_target=list(self.gesture_target) if self.gesture_target else None)


def main():
 rows = []
 # Native initializer -> native registration -> recorded request -> manual delivery.
 for main_thread, button_ok, pan_mode in (
     [(True, b, p) for b in (False, True) for p in ('ready', 'alloc_nil', 'init_nil')]
     + [(False, True, 'ready'), (False, False, 'ready')]):
  model = Bubble(main_thread, button_ok, pan_mode)
  model.prepare()
  before = model.snapshot()
  assert before['flags'] == 1 and before['button'] == '0x0'
  returned = model.invoke('v58InstallBubble:')
  assert returned == SELF
  initial = model.snapshot()
  assert bool(model.e.q(UI_STATE)) == (main_thread and button_ok)
  if main_thread and button_ok:
   assert initial['flags'] == (15 if pan_mode == 'ready' else 7)
   assert model.parent == SELF and model.center == (80., 112.)
  else:
   assert initial['flags'] == 1 and model.parent == 0
  event_count = len(model.ui_events)
  if not main_thread:
   model.ui_main = True  # Explicit second delivery; not automatic retry.
   model.invoke('v58InstallBubble:')
   assert bool(model.e.q(UI_STATE)) == button_ok
  after = model.snapshot()
  prior_allocations = sum(v['selector'] == 'buttonWithType:' for v in model.ui_events)
  model.invoke('v58InstallBubble:')
  final_allocations = sum(v['selector'] == 'buttonWithType:' for v in model.ui_events)
  assert final_allocations-prior_allocations == int(not button_ok)
  rows.append(dict(test='initializerRequestAndManualInstall', main_thread=main_thread,
                   button_ok=button_ok, pan_mode=pan_mode, before_delivery=before,
                   after_first_delivery=initial, after_explicit_main_delivery=after,
                   events=model.ui_events, first_delivery_event_count=event_count,
                   callback_delivery='manual, after native initializer return',
                   method_imp={k:hex(v) for k,v in model.methods.items()}))
 # Native tap callback is a concrete pointee writer, distinct from shortcut set-1.
 for initial_byte in (None, 0, 1, 2, 255):
  model = Bubble()
  model.prepare(0 if initial_byte is None else CONTROL_A)
  model.invoke('v58InstallBubble:')
  if initial_byte is not None:
   model.e.write(CONTROL_A, bytes([initial_byte]))
  values = []
  for _ in range(2):
   model.invoke('v58TapBubble:', BUTTON)
   values.append(model.e.byte(CONTROL_A))
  assert values == ([0, 0] if initial_byte is None else [initial_byte ^ 1, initial_byte])
  assert int.from_bytes(model.e.u.mem_read(UI_STATE+0x24, 4), 'little') == 2
  rows.append(dict(test='nativeTapPointeeWriter', initial_byte=initial_byte,
                   pointer_nil=initial_byte is None, bytes_after_taps=values,
                   tap_counter=2, actual_ui_delivery=False))
 # Compose real once/factory reuse with the newly executed control-byte writer.
 model = Bubble()
 model.prepare(factory=True)
 for pointer in (CONTROL_B, 0):
  model.fp(0., 0., 320., 240.)
  assert model.nested(0x68401c, [(0, OVERLAYCLASS), (2, pointer),
                               (3, 0), (4, 0), (5, 0)]) == SELF
 model.invoke('v58InstallBubble:')
 model.invoke('v58TapBubble:', BUTTON)
 assert model.e.q(0x1011e20) == CONTROL_A
 assert model.e.byte(CONTROL_A) == 1 and model.e.byte(CONTROL_B) == 0
 assert len(model.requests) == 1
 rows.append(dict(test='singletonFirstControlAndNativeTap',
                  later_inputs=['different mapped pointer', 'nil'],
                  first_control_byte=1, later_control_byte=0,
                  initialization_requests=len(model.requests),
                  real_pointer_change_or_lifetime_established=False))
 # Pan callback state gates, translation consumption and native clamp composition.
 for state, cached, small in ([(s, True, False) for s in range(6)] +
                              [(2, False, False), (2, True, True)]):
  model = Bubble()
  model.prepare()
  model.invoke('v58InstallBubble:')
  model.gesture_state = state
  if not cached:
   putq(model.e, UI_STATE, 0)
  if small:
   model.bounds = (0., 0., 63., 240.)
  before = model.center
  start = len(model.ui_events)
  model.invoke('v58PanBubble:', PAN)
  accepted = cached and state in (1, 2, 3)
  count = int.from_bytes(model.e.u.mem_read(UI_STATE+0x28, 4), 'little')
  assert count == int(accepted)
  assert model.translation == ((0., 0.) if accepted else (800., -800.))
  assert model.center == ((288., 32.) if accepted and not small else before)
  rows.append(dict(test='nativePanStateAndClamp', gesture_state=state,
                   cached=cached, bounds=list(model.bounds), center_before=list(before),
                   center_after=list(model.center), translation_after=list(model.translation),
                   pan_counter=count, events=model.ui_events[start:],
                   real_touch_delivery=False))
 assert len(rows) == 22
 windows = []
 for lo, hi in ((0x1016700, 0x1016820), (0x1016820, 0x1016a7c),
                (0x1016a80, 0x1016ab0), (0x1016ab0, 0x1016b54),
                (0x1016b60, 0x1016c18)):
  windows.append(dict(start=hex(lo), end_exclusive=hex(hi),
                      r03_sha256=hashlib.sha256(P.bytes(lo, hi-lo)).hexdigest()))
 data = dict(passed=True, cases=len(rows),
             scope='22 R03 native/model records. Native Overlay normal return and registration fill cold UI caches and expose existing install/tap/pan IMPs; requested callback delivered manually. UIKit/ObjC/ARC, allocation, class/method-add success and main-thread answers modeled. Native factory/once reuse retains first mapped control and actual native tap XOR-writes its byte. Gesture states, nil allocations, changed pointer inputs and small geometry synthetic. No real scheduling, method installation, touch/GPU/device run, pointer lifetime/race proof or performance result. No binary edits.',
             input_sha256={'original':hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),
                           'r03':hashlib.sha256(R03.read_bytes()).hexdigest()},
             native_windows=windows, records=rows)
 (RESULTS/'bubble-callback-tests.json').write_text(json.dumps(data, separators=(',', ':'))+'\n')
 print(json.dumps(dict(passed=True, cases=len(rows), native_windows=len(windows))))


if __name__ == '__main__':
 main()