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

level = 1
score = 0
target_carrots = 3

ui_level = label(
    pos=vector(-5, 5.5, 0),
    text=f"LEVEL: {level}",
    height=20,
    color=color.yellow,
    box=False,
)
ui_score = label(
    pos=vector(0, 5.5, 0),
    text=f"🥕 Wortel: {score}/{target_carrots}",
    height=20,
    color=vector(1, 0.8, 0.2),
    box=False,
)
ui_info = label(
    pos=vector(0, -5.5, 0),
    text="[Panah]: Jalan | [Spasi]: Lompat | [F/J]: Tebasan Energi!",
    height=16,
    color=color.white,
    box=False,
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
# 3. KELINCI (HERO) & EFFECT SERANGAN
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

# Efek visual tebasan pedang/energi
slash_effect = ring(
    pos=vector(0, 0.8, 0),
    axis=vector(0, 1, 0),
    radius=1.2,
    thickness=0.1,
    color=vector(1, 0.3, 0.6),
)
slash_effect.visible = False

# Bar Darah Player (Hijau)
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


# ---------------------------------------------------------
# 4. MUSUH & HEALTH BAR
# ---------------------------------------------------------
enemy_max_hp = 50
enemy_hp = 50
enemy_speed = 0.05
enemy_alive = True
dark_gray_color = vector(0.3, 0.3, 0.3)

e_body = sphere(pos=vector(0, 0.7, 0), radius=0.7, color=dark_gray_color)
e_head = sphere(pos=vector(0, 1.3, 0.4), radius=0.45, color=dark_gray_color)
e_eye1 = sphere(pos=vector(-0.15, 1.45, 0.75), radius=0.07, color=color.red)
e_eye2 = sphere(pos=vector(0.15, 1.45, 0.75), radius=0.07, color=color.red)
e_horn1 = cone(
    pos=vector(-0.2, 1.6, 0.3),
    axis=vector(-0.1, 0.5, 0),
    radius=0.08,
    color=color.black,
)
e_horn2 = cone(
    pos=vector(0.2, 1.6, 0.3),
    axis=vector(0.1, 0.5, 0),
    radius=0.08,
    color=color.black,
)

enemy = compound([e_body, e_head, e_eye1, e_eye2, e_horn1, e_horn2])
enemy.pos = vector(4, 0.5, 4)

enemy_hp_bg = box(
    pos=vector(0, 2.5, 0), size=vector(1.4, 0.15, 0.1), color=color.gray(0.3)
)
enemy_hp_bar = box(
    pos=vector(0, 2.5, 0), size=vector(1.4, 0.16, 0.12), color=color.red
)


def update_enemy_hp():
  if not enemy_alive:
    enemy_hp_bar.visible = False
    enemy_hp_bg.visible = False
    return
  ratio = max(0, enemy_hp / enemy_max_hp)
  enemy_hp_bar.size.x = 1.4 * ratio
  enemy_hp_bar.pos = enemy.pos + vector(-0.7 * (1 - ratio), 2.1, 0)
  enemy_hp_bg.pos = enemy.pos + vector(0, 2.1, 0)


# ---------------------------------------------------------
# 5. OBJECT WORTEL
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

# ---------------------------------------------------------
# 6. LOOP UTAMA GAME
# ---------------------------------------------------------
while True:
  rate(60)
  t += 0.15
  k = keysdown()

  if player_hp <= 0:
    ui_info.text = "💀 GAME OVER! Kelinci kamu kalah... Jalankan ulang script!"
    ui_info.color = color.red
    break

  # A. KONTROL PLAYER
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

  # TOMBOL SERANG (F atau J)
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

  # ANIMASI SERANGAN TEBASAN ENERGI
  if is_attacking:
    rabbit.rotate(angle=0.4, axis=vector(0, 1, 0))
    # Tampilkan Efek Tebasan Melingkar
    slash_effect.visible = True
    slash_effect.pos = rabbit.pos + vector(0, 0.3, 0)
    slash_effect.radius = 1.2 + (12 - attack_timer) * 0.08  # Melebar keluar

    attack_timer -= 1

    # Cek Hitbox Serangan ke Musuh
    if enemy_alive and (rabbit.pos - enemy.pos).mag < 2.0:
      enemy_hp -= 3.0
      update_enemy_hp()
      enemy.pos += (enemy.pos - rabbit.pos).norm() * 0.25  # Terlempar mundur
      if enemy_hp <= 0:
        enemy_alive = False
        enemy.visible = False

    if attack_timer <= 0:
      is_attacking = False
      slash_effect.visible = False

  # Gravitasi & Lompat
  rabbit.pos.y += velocity_y
  velocity_y += gravity
  if rabbit.pos.y <= 0.5:
    rabbit.pos.y = 0.5
    velocity_y = 0
    is_jumping = False

  update_player_hp()

  # B. AI MUSUH
  if enemy_alive:
    dir_to_player = (rabbit.pos - enemy.pos).norm()
    enemy.pos += dir_to_player * enemy_speed
    enemy.pos.y = 0.5
    enemy.axis = dir_to_player * 1.4

    update_enemy_hp()

    if (rabbit.pos - enemy.pos).mag < 1.1:
      player_hp -= 0.7
      update_player_hp()

  # C. SISTEM WORTEL, HEAL, & LEVEL UP
  if carrot:
    carrot.pos.y = 0.4 + math.sin(t) * 0.1
    carrot.rotate(angle=0.04, axis=vector(0, 1, 0))

    if (rabbit.pos - carrot.pos).mag < 1.1 and not eating_anim:
      score += 1
      ui_score.text = f"🥕 Wortel: {score}/{target_carrots}"

      # FITUR 1: DARAH NAİK PAS MAKAN WORTEL (+20 HP)
      player_hp = min(player_max_hp, player_hp + 20)
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

      # Naik Level jika target wortel tercapai & musuh mati
      if score >= target_carrots and not enemy_alive:
        level += 1
        score = 0
        target_carrots += 2

        # FITUR 2: DARAH FULL AGAIN PAS NAIK LEVEL!
        player_hp = player_max_hp
        update_player_hp()

        enemy_max_hp += 35
        enemy_hp = enemy_max_hp
        enemy_speed += 0.02

        ui_level.text = f"LEVEL: {level}"
        ui_score.text = f"🥕 Wortel: {score}/{target_carrots}"
        ui_info.text = (
            f"🎉 NAIK LEVEL {level}! Darah kamu kembali FULL! Musuh makin kuat!"
        )

        enemy_alive = True
        enemy.visible = True
        enemy.pos = vector(random.choice([-5, 5]), 0.5, random.choice([-5, 5]))
        carrot = spawn_carrot()
      else:
        carrot = spawn_carrot()