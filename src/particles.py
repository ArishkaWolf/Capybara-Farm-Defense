import random

import pygame

from .constants import COLORS


class Particle:
    def __init__(self, pos, color, velocity=None, life=0.65, radius=4):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(velocity or (random.uniform(-55, 55), random.uniform(-85, -20)))
        self.life = life
        self.max_life = life
        self.radius = radius
        self.color = color

    def update(self, dt):
        self.life -= dt
        self.vel.y += 150 * dt
        self.pos += self.vel * dt

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = max(0, min(255, int(255 * self.life / self.max_life)))
        color = (*self.color, alpha)
        size = max(1, int(self.radius * self.life / self.max_life))
        layer = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        pygame.draw.circle(layer, color, (size * 2, size * 2), size)
        surface.blit(layer, (self.pos.x - size * 2, self.pos.y - size * 2))


class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.attack_lines = []

    def burst(self, pos, color, amount=8):
        for _ in range(amount):
            self.particles.append(Particle(pos, color))

    def resource_collect(self, pos, resource):
        color = COLORS.get(resource, COLORS["coin"])
        self.burst(pos, color, 12)

    def attack(self, start, end, color=(255, 244, 168)):
        self.attack_lines.append([pygame.Vector2(start), pygame.Vector2(end), color, 0.16])
        for _ in range(4):
            self.particles.append(Particle(end, color, life=0.32, radius=3))

    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]
        for line in self.attack_lines:
            line[3] -= dt
        self.attack_lines = [line for line in self.attack_lines if line[3] > 0]

    def draw(self, surface):
        for start, end, color, life in self.attack_lines:
            pygame.draw.line(surface, color, start, end, max(1, int(5 * life / 0.16)))
        for particle in self.particles:
            particle.draw(surface)
