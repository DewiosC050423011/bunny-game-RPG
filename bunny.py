import math
import random
from vpython import (
    box,
    canvas,
    color,
    compound,
    cone,
    cylinder,
    keysdown,
    label,
    rate,
    ring,
    sphere,
    vector,
    winput,
)

# ---------------------------------------------------------
# 1. SETUP SCENE & UI GAME
# ---------------------------------------------------------
scene = canvas(
    title="",
    width=1200,
    height=700,
    background=vector(0.08, 0.12, 0.2),
)

# Prompt Nama Karakter
player_name = "Dewi"

game_state = "START"  # "START", "TUTORIAL_MENU", "PLAYING", "PAUSED", "GAMEOVER"
level = 1
score = 0
target_carrots = 3
is_tutorial = False

# UI LEVEL (Pojok Kiri Dalam Arena)
ui_level = label(
    pos=vector(-7.5, 4.5, -6),
    text=f"LEVEL: {level}",
    height=20,
    color=color.yellow,
    box=False,
)

# UI SCORE (Pojok Kanan Dalam Arena)
ui_score = label(
    pos=vector(7.5, 4.5, -6),
    text=f"🥕 Wortel: {score}/{target_carrots}",
    height=20,
    color=vector(1, 0.8, 0.2),
    box=False,
)

# Text Banner Tengah
banner_ui = label(
    pos=vector(0, 2, 0),
    text=(
        "🐰 GAME KELINCI 3D RPG 🐰\n\nTekan [ENTER] untuk Input Nama & Mulai"
    ),
    height=26,
    color=color.cyan,
    box=True,
    border=6,
)

# 2. ARENA BERMAIN
ground = box(
    pos=vector(0, -0.5, 0),
    size=vector(18, 0.2, 18),
    color=vector(0.18, 0.4, 0.2),
)


def make_tree(x, z):
  cylinder(
      pos=vector(x, -0.4, z),
      axis=vector(0, 1.5, 0),
      radius=0.2,
      color=vector(0.4, 0.2, 0.1),
  )
  cone(
      pos=vector(x, 0.6, z),
      axis=vector(0, 1.8, 0),
      radius=1.1,
      color=vector(0.1, 0.35, 0.15),
  )


for px in [-7.5, 7.5]:
  for pz in range(-7, 8, 3):
    make_tree(px, pz)
    make_tree(pz, px)

# ---------------------------------------------------------
# 3. KELINCI (HERO), NAMA, & EFEEKS
# ---------------------------------------------------------
player_max_hp = 100
player_hp = 100

body = sphere(pos=vector(0, 0.8, 0), radius=0.8, color=color.white)
head = sphere(pos=vector(0, 1.5, 0.3), radius=0.5, color=color.white)
eye_l = sphere(pos=vector(-0.18, 1.65, 0.7), radius=0.08, color=color.black)
eye_r = sphere(pos=vector(0.18, 1.65, 0.7), radius=0.08, color=color.black)
nose = sphere(pos=vector(0, 1.5, 0.78), radius=0.07, color=color.red)
ear_l = cylinder(
    pos=vector(-0.25, 1.8, 0.3),
    axis=vector(-0.1, 0.8, -0.1),
    radius=0.11,
    color=color.white,
)
ear_r = cylinder(
    pos=vector(0.25, 1.8, 0.3),
    axis=vector(0.1, 0.8, -0.1),
    radius=0.11,
    color=color.white,
)

rabbit = compound([body, head, eye_l, eye_r, nose, ear_l, ear_r])
rabbit.pos = vector(0, 0.5, 0)

# Label Nama Karakter di Atas Kelinci
name_label = label(
    pos=rabbit.pos + vector(0, 3.2, 0),
    text=f"👑 {player_name}",
    height=16,
    color=color.cyan,
    box=False,
)

slash_effect = ring(
    pos=vector(0, 0.8, 0),
    axis=vector(0, 1, 0),
    radius=1.2,
    thickness=0.1,
    color=vector(1, 0.3, 0.6),
)
slash_effect.visible = False

player_hp_bg = box(
    pos=vector(0, 2.8, 0), size=vector(1.6, 0.15, 0.1), color=color.gray(0.3)
)
player_hp_bar = box(
    pos=vector(0, 2.8, 0), size=vector(1.6, 0.16, 0.12), color=color.green
)


def update_player_hp():
  ratio = max(0, player_hp / player_max_hp)
  player_hp_bar.size.x = 1.6 * ratio
  player_hp_bar.pos = rabbit.pos + vector(-0.8 * (1 - ratio), 2.3, 0)
  player_hp_bg.pos = rabbit.pos + vector(0, 2.3, 0)
  name_label.pos = rabbit.pos + vector(0, 2.9, 0)


# ---------------------------------------------------------
# 4. SISTEM MULTIPLE ENEMIES & BOSS
# ---------------------------------------------------------
enemies = []
dark_gray_color = vector(0.3, 0.3, 0.3)


class Enemy:

  def __init__(self, is_boss=False):
    self.is_boss = is_boss
    self.max_hp = 200 if is_boss else 50 + (level * 10)
    self.hp = self.max_hp
    self.speed = 0.035 if is_boss else 0.045 + (level * 0.005)

    scale = 1.8 if is_boss else 1.0
    body_color = vector(0.7, 0.1, 0.1) if is_boss else dark_gray_color

    eb = sphere(pos=vector(0, 0.7 * scale, 0), radius=0.7 * scale, color=body_color)
    eh = sphere(
        pos=vector(0, 1.3 * scale, 0.4 * scale),
        radius=0.45 * scale,
        color=body_color,
    )
    ee1 = sphere(
        pos=vector(-0.15 * scale, 1.45 * scale, 0.75 * scale),
        radius=0.08 * scale,
        color=color.yellow if is_boss else color.red,
    )
    ee2 = sphere(
        pos=vector(0.15 * scale, 1.45 * scale, 0.75 * scale),
        radius=0.08 * scale,
        color=color.yellow if is_boss else color.red,
    )
    eh1 = cone(
        pos=vector(-0.2 * scale, 1.6 * scale, 0.3 * scale),
        axis=vector(-0.1, 0.5 * scale, 0),
        radius=0.08 * scale,
        color=color.black,
    )
    eh2 = cone(
        pos=vector(0.2 * scale, 1.6 * scale, 0.3 * scale),
        axis=vector(0.1, 0.5 * scale, 0),
        radius=0.08 * scale,
        color=color.black,
    )

    self.obj = compound([eb, eh, ee1, ee2, eh1, eh2])
    self.obj.pos = vector(
        random.choice([-6, 6]), 0.5 * scale, random.choice([-6, 6])
    )

    # Efek Serangan Musuh (Aura Merah)
    self.attack_ring = ring(
        pos=self.obj.pos,
        axis=vector(0, 1, 0),
        radius=1.2 * scale,
        thickness=0.08,
        color=color.red,
    )
    self.attack_ring.visible = False

    self.hp_bg = box(
        pos=vector(0, 2.5 * scale, 0),
        size=vector(1.4 * scale, 0.15, 0.1),
        color=color.gray(0.3),
    )
    self.hp_bar = box(
        pos=vector(0, 2.5 * scale, 0),
        size=vector(1.4 * scale, 0.16, 0.12),
        color=color.red,
    )
    self.alive = True

  def update_hp(self):
    if not self.alive:
      self.hp_bar.visible = False
      self.hp_bg.visible = False
      self.attack_ring.visible = False
      return
    ratio = max(0, self.hp / self.max_hp)
    scale = 1.8 if self.is_boss else 1.0
    self.hp_bar.size.x = 1.4 * scale * ratio
    self.hp_bar.pos = self.obj.pos + vector(
        -0.7 * scale * (1 - ratio), 2.1 * scale, 0
    )
    self.hp_bg.pos = self.obj.pos + vector(0, 2.1 * scale, 0)


def spawn_enemies():
  global enemies
  for e in enemies:
    e.alive = False
    e.update_hp()
    e.obj.visible = False
  enemies.clear()

  if is_tutorial:
    enemies.append(Enemy(is_boss=False))
  elif level % 3 == 0:  # BOSS LEVEL setiap 3 level!
    enemies.append(Enemy(is_boss=True))
  else:
    count = min(4, level)  # Jumlah musuh nambah tiap level
    for _ in range(count):
      enemies.append(Enemy(is_boss=False))


# ---------------------------------------------------------
# 5. SISTEM WORTEL & RESET
# ---------------------------------------------------------
def spawn_carrot():
  cb = cone(
      pos=vector(0, 0, 0), axis=vector(0, 0.7, 0), radius=0.2, color=color.orange
  )
  cl = cylinder(
      pos=vector(0, 0.7, 0),
      axis=vector(0, 0.25, 0),
      radius=0.05,
      color=color.green,
  )
  c = compound([cb, cl])
  c.pos = vector(random.uniform(-5.5, 5.5), 0.3, random.uniform(-5.5, 5.5))
  return c


carrot = spawn_carrot()


def reset_level():
  global player_hp, score, carrot
  player_hp = player_max_hp
  rabbit.pos = vector(0, 0.5, 0)
  score = 0
  ui_level.text = f"LEVEL: {'TUTORIAL' if is_tutorial else level}"
  ui_score.text = f"🥕 Wortel: {score}/{target_carrots}"
  update_player_hp()
  spawn_enemies()
  if carrot:
    carrot.visible = False
  carrot = spawn_carrot()


def reset_full_game():
  global level, target_carrots, is_tutorial
  is_tutorial = False
  level = 1
  target_carrots = 3
  reset_level()


eating_anim = False
anim_timer = 0
anim_carrot = None

speed = 0.14
velocity_y = 0
gravity = -0.015
is_jumping = False
is_attacking = False
attack_timer = 0
t = 0
current_angle = 0
pause_debounce = False

# ---------------------------------------------------------
# 6. LOOP UTAMA GAME
# ---------------------------------------------------------
while True:
  rate(60)
  k = keysdown()

  if game_state == "START":
    if "\n" in k or "enter" in k:
      game_state = "TUTORIAL_MENU"
      banner_ui.text = (
          "📚 PILIH MODE 📚\n\nTekan [T] : Main Level Tutorial\nTekan [S] :"
          " Skip / Langsung Level 1"
      )
    continue

  elif game_state == "TUTORIAL_MENU":
    if "t" in k:
      is_tutorial = True
      target_carrots = 1
      reset_level()
      game_state = "PLAYING"
      banner_ui.visible = False
    elif "s" in k:
      reset_full_game()
      game_state = "PLAYING"
      banner_ui.visible = False
    continue

  elif game_state == "PAUSED":
    if "p" in k and not pause_debounce:
      pause_debounce = True
      game_state = "PLAYING"
      banner_ui.visible = False
    elif "p" not in k:
      pause_debounce = False
    continue

  elif game_state == "GAMEOVER":
    if "r" in k:
      reset_level()
      game_state = "PLAYING"
      banner_ui.visible = False
    elif "\n" in k or "enter" in k:
      reset_full_game()
      game_state = "PLAYING"
      banner_ui.visible = False
    continue

  # -----------------------------------------------------
  # STATE: PLAYING
  # -----------------------------------------------------
  if "p" in k and not pause_debounce:
    pause_debounce = True
    game_state = "PAUSED"
    banner_ui.text = "⏸ GAME PAUSED\nTekan [P] untuk Lanjut"
    banner_ui.visible = True
    continue
  elif "p" not in k:
    pause_debounce = False

  t += 0.15
  if "r" in k:
    reset_level()

  # A. MOVEMENT & ATTACK PLAYER
  move_x, move_z = 0, 0
  if "up" in k:
    move_z -= speed
  if "down" in k:
    move_z += speed
  if "left" in k:
    move_x -= speed
  if "right" in k:
    move_x += speed

  if " " in k and not is_jumping:
    velocity_y = 0.35
    is_jumping = True

  if ("f" in k or "j" in k) and not is_attacking:
    is_attacking = True
    attack_timer = 12

  rabbit.pos.x = max(-6.5, min(6.5, rabbit.pos.x + move_x))
  rabbit.pos.z = max(-6.5, min(6.5, rabbit.pos.z + move_z))

  if move_x != 0 or move_z != 0:
    target_angle = math.atan2(move_x, move_z)
    diff = math.atan2(
        math.sin(target_angle - current_angle),
        math.cos(target_angle - current_angle),
    )
    current_angle += diff * 0.2
    rabbit.axis = vector(
        math.sin(current_angle), 0, math.cos(current_angle)
    ) * 1.6

  # PLAYER ATTACK LOGIC
  if is_attacking:
    rabbit.rotate(angle=0.4, axis=vector(0, 1, 0))
    slash_effect.visible = True
    slash_effect.pos = rabbit.pos + vector(0, 0.3, 0)
    slash_effect.radius = 1.2 + (12 - attack_timer) * 0.08
    attack_timer -= 1

    for e in enemies:
      if e.alive and (rabbit.pos - e.obj.pos).mag < (2.2 if e.is_boss else 1.8):
        e.hp -= 4.0
        e.update_hp()
        e.obj.pos += (e.obj.pos - rabbit.pos).norm() * 0.2
        if e.hp <= 0:
          e.alive = False
          e.obj.visible = False
          e.update_hp()

    if attack_timer <= 0:
      is_attacking = False
      slash_effect.visible = False

  # GRAVITASI
  rabbit.pos.y += velocity_y
  velocity_y += gravity
  if rabbit.pos.y <= 0.5:
    rabbit.pos.y = 0.5
    velocity_y = 0
    is_jumping = False

  update_player_hp()

  if player_hp <= 0:
    game_state = "GAMEOVER"
    banner_ui.text = (
        "💀 GAME OVER!\nTekan [R] Restart Level\nTekan [ENTER] New Game"
    )
    banner_ui.visible = True
    continue

  # B. AI ENEMIES & ANIMASI SERANGAN MUSUH
  all_enemies_dead = True
  for e in enemies:
    if e.alive:
      all_enemies_dead = False
      dir_to_player = (rabbit.pos - e.obj.pos).norm()
      e.obj.pos += dir_to_player * e.speed
      e.obj.axis = dir_to_player * (2.2 if e.is_boss else 1.4)
      e.update_hp()

      dist = (rabbit.pos - e.obj.pos).mag
      # Animasi Serangan Musuh (Aura Merah Menyala)
      if dist < 1.6:
        e.attack_ring.visible = True
        e.attack_ring.pos = e.obj.pos
        player_hp -= 1.2 if e.is_boss else 0.6
        update_player_hp()
      else:
        e.attack_ring.visible = False

  # C. WORTEL & NAIK LEVEL
  if carrot:
    carrot.pos.y = 0.4 + math.sin(t) * 0.1
    carrot.rotate(angle=0.04, axis=vector(0, 1, 0))

    if (rabbit.pos - carrot.pos).mag < 1.1 and not eating_anim:
      score += 1
      ui_score.text = f"🥕 Wortel: {score}/{target_carrots}"
      player_hp = min(player_max_hp, player_hp + 25)
      update_player_hp()

      anim_carrot = carrot
      eating_anim = True
      anim_timer = 0
      carrot = None

  if eating_anim and anim_carrot:
    anim_timer += 1
    anim_carrot.pos.y += 0.1
    anim_carrot.rotate(angle=0.4, axis=vector(0, 1, 0))
    anim_carrot.size *= 1.05

    if anim_timer > 15:
      anim_carrot.visible = False
      eating_anim = False
      anim_carrot = None

      if score >= target_carrots and all_enemies_dead:
        if is_tutorial:
          is_tutorial = False
          level = 1
          target_carrots = 3
        else:
          level += 1
          target_carrots += 2

        reset_level()
      else:
        carrot = spawn_carrot()