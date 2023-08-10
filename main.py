import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

#nome da janela do jogo
pygame.display.set_caption("Um joguinho ai")

#bg_color = (255, 255, 255) usado só para teste inicial da janela
width_, height_ = 1000, 800 #altura e largura da tela inicial do jogo
fps = 60
player_vel = 5 #velocidade do jogador

window = pygame.display.set_mode((width_,height_))# configuração da tela em uma variavel

#----------------------------------------------------#

def flip(sprites): #mudar a direção das sprites(imagens)
    return[pygame.transform.flip(sprite, True, False) for sprite in sprites] #True ele vai virar a sprite em uma direção e falso vai voltar para a posição "original"

def carregar_sprites(dir1, dir2, width, height, direction_=False):#deixar os arquivos com facil acesso
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    todas_sprites = {}

    for image in images:
        sprite_ = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_.get_width() // width):
            superficie = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            superficie.blit(sprite_, (0,0), rect)
            sprites.append(pygame.transform.scale2x(superficie))
        
        if direction_:
            todas_sprites[image.replace(".png", "") + "_direita"] = sprites #gerar os arquivos com seus devidos direcionamentos
            todas_sprites[image.replace(".png", "") + "_esquerda"] = flip(sprites)
        else:
            todas_sprites[image.replace(".png", "")] = sprites

    return todas_sprites

def get_block(size):
    path = join("assets", "Terrain","Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size) #posição do terreno na sprite
    surface.blit(image, (0,0),rect)
    return pygame.transform.scale2x(surface)


            
#criar jogador, nesse caso sera usado a classe sprite do pygame para checar colisão
class Player(pygame.sprite.Sprite):
    cor = (255,0,0)
    gravidade = 1 #sim o jogo tem gravidade no jogador, se ele cair de um lugar alto ele vai cair e acelerar
    sprites_jogador = carregar_sprites("MainCharacters", "NinjaFrog", 32, 32, True) #carregar os personagens "dinamicamente", o True serve para funcionar o multidirecional
    delay_animacao = 3
    def __init__(self, x, y, width,height):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direcao = "esquerda"
        self.animation_count = 0
        self.queda_count = 0
        self.pulo_count = 0
        self.hit = False
        self.hit_count = 0


    def pulo(self):
        self.y_vel = -self.gravidade * 8
        self.animation_count = 0
        self.pulo_count += 1
        if self.pulo_count == 1:
            self.queda_count = 0

    def receber_hit(self):
        self.hit = True
        self.hit_count = 0

    def movimento(self,dx,dy):#dx dy = direction
        self.rect.x += dx
        self.rect.y += dy

    def mover_esquerda(self,vel):
        self.x_vel = -vel
        if self.direcao != "esquerda": #isso serve para checar o lado que o personagem esta olhando para aplicar as animaçoes corretamente
            self.direcao = "esquerda"
            self.animation_count = 0

    def mover_direita(self,vel):
        self.x_vel = vel
        if self.direcao != "direita": #isso serve para checar o lado que o personagem esta olhando para aplicar as animaçoes corretamente
            self.direcao = "direita"
            self.animation_count = 0
    
    def loop(self,fps):
        self.y_vel += min(1,(self.queda_count / fps) * self.gravidade) #seta gravidade on/off manualmente no codigo
        self.movimento(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0


        self.update_sprite()

        self.queda_count += 1
    def pousou(self):
        self.queda_count = 0
        self.y_vel = 0
        self.pulo_count = 0 #falta fazer


    def hit_cabc(self):
        self.contar = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite = "idle"
        if self.hit:
            sprite = "hit"
        if self.y_vel < 0:
            if self.pulo_count == 1:
                sprite = "jump"
            elif self.pulo_count == 2:
                sprite = "double_jump"
        elif self.y_vel > self.gravidade * 2:
            sprite = "fall"
        elif self.x_vel != 0:
            sprite = "run"

        sprite_nome = sprite + "_" + self.direcao
        sprites = self.sprites_jogador[sprite_nome]
        sprite_index = (self.animation_count // self.delay_animacao) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, windo, offset_x):
        #pygame.draw.rect(windo,self.cor, self.rect) # retangulo de teste
        #self.sprite = self.sprites_jogador["idle_" + self.direcao][0] #removido
        windo.blit(self.sprite,(self.rect.x - offset_x, self.rect.y))

#classe para criar objetos

class Objects():
    def __init__(self,x,y,width,height,name=None):
            super().__init__()
            self.rect = pygame.Rect(x,y,width,height)
            self.image = pygame.Surface((width, height),pygame.SRCALPHA)
            self.width = width
            self.height = height
            self.name = name

    def draw(self,windo, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Objects):
    def __init__(self, x,y,size):
        super().__init__(x,y,size,size)
        block = get_block(size)
        self.image.blit(block,(0,0)) #display na tela
        self.mask = pygame.mask.from_surface(self.image) #usado para contar hitbox


class Fogo(Objects):

    delay_animacao = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fogo")
        self.fogo = carregar_sprites("Traps", "Fire", width, height)
        self.image = self.fogo["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def aceso(self):
        self.animation_name = "on"

    def apagado(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fogo[self.animation_name]
        sprite_index = (self.animation_count // self.delay_animacao) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        #evitar lag no fogo resetando a animação, o player a gente reseta o tempo todo com jump por exemplo mas aq é manual
        if self.animation_count // self.delay_animacao > len(sprites):
            self.animation_count = 0

#função para configurar o fundo de tela
def get_bg(name):
    image = pygame.image.load(join("assets", "Background", name))
    _,_, width,height = image.get_rect()
    tiles = []
    #calcular dinamicamente o tamanho das imgs de background e preencher a tela inteira
    for i in range(width_ // width + 1):
        for j in range(height_ // height + 1):
            position = (i * width, j * height) #funciona com tuple -> [i*width, j* height]
            tiles.append(position)
    return tiles, image

#função para desenhar o background na tela
def draw(window, background, bg_img, player, objects, offset_x):
    for tile in background:
        window.blit(bg_img, tile) #para funcionar com tuple -> tuple(tile)

    for obj in objects:
        obj.draw(window, offset_x)

    
    player.draw(window, offset_x)

    pygame.display.update()

def cuidar_colisao_vert(player,objects,dy):
    colidir_objetos = []
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.pousou()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_cabc()

        colidir_objetos.append(obj)
#lidar com a colisao horizontal
def colidir(player, objects, dx):
    player.movimento(dx, 0)
    player.update()
    colidir_objetos = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            colidir_objetos = obj
            break

    player.movimento(-dx, 0)
    player.update()
    return colidir_objetos


#função para cuidar da movimentação do personagem
def cuidar_movimentacao(player, objects):
    teclas = pygame.key.get_pressed()

    player.x_vel = 0 #se não configurar a velocidade para 0 aqui ele vai mover e manter a direção de movimento ate troca de tecla
    colidir_esquerda = colidir(player, objects, -player_vel * 2)
    colidir_direita = colidir(player, objects, player_vel * 2)
    if teclas[pygame.K_a] and not colidir_esquerda:
        player.mover_esquerda(player_vel)
    if teclas[pygame.K_d] and not colidir_direita:
        player.mover_direita(player_vel)

    colidir_vertical = [cuidar_colisao_vert(player, objects, player.y_vel)]
    
    checar = [colidir_esquerda, colidir_direita, *colidir_vertical]

    for obj in checar:
        if obj and obj.name == "fogo":
            player.receber_hit()

#função para gerar a tela e o jogo
def main(window):
    clock = pygame.time.Clock()
    background, bg_img = get_bg("Green.png") #coletar a configuração do background

    block_size = 96
    player = Player(100,100,50,50) # mostrar jogador na tela

    fogo = Fogo(100, height_ - block_size - 64, 16, 32)
    fogo.aceso()
    #arrumando a velocidade do frames para estabilizar dependendo do pc

    
    floor = [Block(i * block_size, height_ - block_size, block_size) for i in range(-width_ // block_size, width_ * 2 //  block_size)]

    #blocos = [Block(0, height_ - block_size, block_size)] # faz 1 bloco

    objects = [*floor,Block(0,height_ - block_size * 2, block_size), Block(block_size * 3, height_ - block_size * 4, block_size), fogo]

    offset_x = 0
    scroll_area_w = 200

    run = True
    while run:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: #checa se o jogador clicou para fechar o jogo
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.pulo_count < 2:
                    player.pulo()  

        player.loop(fps) #checa posição atual
        fogo.loop()
        cuidar_movimentacao(player, objects) #verifica input para onde ira mover
        draw(window, background, bg_img, player, objects, offset_x) #mostra na tela/ muda local do player e outros aspectos

        if ((player.rect.right - offset_x >= width_ - scroll_area_w) and  player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_w) and player.x_vel < 0):
            offset_x += player.x_vel


    pygame.quit()
    quit()

#garantindo que o arquivo rode corretamente
if __name__ == "__main__":
    main(window)