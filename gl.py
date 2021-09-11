#Codigo ayuda: https://github.com/churly92/Engine3D/blob/main/gl.py
#Repositorio perteneciente a Prof. Carlos Alonso

#Mirka Monzon 18139
#Proyecto 1: Software Renderer 

import struct 
from obj import Obj, Texture
from collections import namedtuple
import random
import math

V2 = namedtuple('Vertex2', ['x', 'y'])
V3 = namedtuple('Vertex3', ['x', 'y', 'z'])

def MM(a,b):
    c = []
    for i in range(0,len(a)):
        temp=[]
        for j in range(0,len(b[0])):
            s = 0
            for k in range(0,len(a[0])):
                s += a[i][k]*b[k][j]
            temp.append(s)
        c.append(temp)
    return c

def char(c):
    return struct.pack('=c', c.encode('ascii'))
def word(c):
    return struct.pack('=h', c)
def dword(c):
    return struct.pack('=l', c)
def color(r, g, b):
    return bytes([b, g, r])

def sum(v0, v1):
    return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)


def sub(v0, v1):
    return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)


def mul(v0, k):
    return V3(v0.x * k, v0.y * k, v0.z * k)


def dot(v0, v1):
    return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z


def length(v0):
    return (v0.x**2 + v0.y**2 + v0.z**2)**0.5


def norm(v0):
    v0length = length(v0)

    if not v0length:
        return V3(0, 0, 0)

    return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)


def cross(u, w):
    return V3(
        u.y * w.z - u.z * w.y,
        u.z * w.x - u.x * w.z,
        u.x * w.y - u.y * w.x,
    )


def bbox(*vertices):
    xs = [vertex.x for vertex in vertices]
    ys = [vertex.y for vertex in vertices]
    xs.sort()
    ys.sort()

    xMin = round(xs[0])
    xMax = round(xs[-1])
    yMin = round(ys[0])
    yMax = round(ys[-1])

    return xMin, xMax, yMin, yMax


def barycentric(A, B, C, P):
    cx, cy, cz = cross(
        V3(B.x - A.x, C.x - A.x, A.x - P.x),
        V3(B.y - A.y, C.y - A.y, A.y - P.y)
    )

    if abs(cz) < 1:
        return -1, -1, -1

    u = cx / cz
    v = cy / cz
    w = 1 - (cx + cy) / cz
    
    return  w, v, u

class Render(object):
    def __init__(self):
        self.framebuffer =[]
        self.zbuffer =[]
        self.active_vertex_array = []
        self.active_texture = None
        self.active_shader = None
        self.light = V3(0,0,1)

    def glInit(self):
        pass

    def clear(self, r, g,b):
        self.framebuffer= [
        [color(r,g,b) for x in range(self.width)]
        for y in range(self.height)
        ]

        self.zbuffer = [
            [-float('inf') for x in range(self.width)]
            for y in range(self.height)
        ]

    def  glClear(self):
        self.clear(0, 0, 0)

    def glClearcolor(self, r, g, b):
        r = round(r*255)
        g = round(g*255)
        b = round(b*255)
        self.clear(r, g, b)

    def glColor(self, r,g,b):
        r = round(r*255)
        g = round(g*255)
        b = round(b*255)
        return color(r, g, b)
        
    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height

    def glViewport(self, x, y, width, height):
        self.viewPortWidth = width
        self.viewPortHeight = height
        self.xViewPort = x
        self.yViewPort = y

    def glVertex(self, x,y):
        calcX = round((x+1)*(self.viewPortWidth/2)+self.xViewPort)
        calcY = round((y+1)*(self.viewPortHeight/2)+self.yViewPort)
        self.point(calcX, calcY)

    def write(self, filename):
        f = open(filename, 'bw')
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))

        #image header 
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        for x in range(self.width):
            for y in range(self.height):
                    f.write(self.framebuffer[y][x])

        f.close()

    def point(self, x, y,mycolor=None):
        try:
            self.framebuffer[x][y] = mycolor
        except:
            pass  

    def glLine(self,x0, y0, x1, y1):
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)
        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        threshold = dx

        y = y0
        for x in range(x0, x1):
            if steep:
                self.point(y, x)
            else:
                self.point(x, y)
            
            offset += dy * 2
            if offset >= threshold:
                y += 1 if y0 < y1 else -1
                threshold += dx * 2

    def glFinish(self, filename='out.bmp'):
        self.write(filename)

    def triangle4(self):
        A = next(self.active_vertex_array)
        B = next(self.active_vertex_array)
        C = next(self.active_vertex_array)

        #print("v",A, B, C)

        if self.active_texture:
            tA = next(self.active_vertex_array)
            tB = next(self.active_vertex_array)
            tC = next(self.active_vertex_array)

            nA = next(self.active_vertex_array)
            nB = next(self.active_vertex_array)
            nC = next(self.active_vertex_array)

        xmin, xmax, ymin, ymax = bbox(A, B, C)

        normal = norm(cross(sub(B, A), sub(C, A)))
        intensity = dot(normal, self.light)
        if intensity < 0:
            return

        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                w, v, u = barycentric(A, B, C, V2(x, y))
                if w < 0 or v < 0 or u < 0:  # 0 is actually a valid value! (it is on the edge)
                    continue

                if self.active_texture:
                    tx = tA.x * w + tB.x * u + tC.x * v
                    ty = tA.y * w + tB.y * u + tC.y * v

                    uncolor = self.active_shader(
                        self,
                        triangle=(A, B, C),
                        bar=(w, v, u),
                        texture_coords=(tx, ty),
                        varying_normals=(nA, nB, nC)
                    )
                
                else:
                    uncolor = color(round(255 * intensity),0,0)

                z = A.z * w + B.z * u + C.z * v

                if x < 0 or y < 0:
                    continue

                if x < len(self.zbuffer) and y < len(self.zbuffer[x]) and z > self.zbuffer[y][x]:
                    self.point(x, y, uncolor)
                    self.zbuffer[y][x] = z


    def transform(self,vertex,translate=(0,0,0),scale=(1,1,1)):
        return V3(
            round((vertex[0]*scale[0])+translate[0]),
            round((vertex[1]* scale[1])+translate[1]),
            round((vertex[2]* scale[2])+translate[2])
        )

    def transform1(self, vertex):
        augmented_vertex = [
            [vertex.x],
            [vertex.y],
            [vertex.z],
            [1]
        ]

        transformed_vertex = MM(self.Projection, self.Viewport)
        transformed_vertex = MM(transformed_vertex, self.View) 
        transformed_vertex = MM(transformed_vertex, self.Model)
        transformed_vertex = MM(transformed_vertex, augmented_vertex)
        
        transformed_vertex = [
            transformed_vertex[0][0],
            transformed_vertex[1][0],
            transformed_vertex[2][0]
        ]
        return V3(*transformed_vertex)


    def load(self, filename, translate, scale, texture=None):
        model = Obj(filename)
        light = V3(0, 0, 1)
        
        for face in model.faces:
            vcount = len(face)
            if vcount == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                A = self.transform(model.vertices[f1],translate,scale)
                B = self.transform(model.vertices[f2],translate,scale)
                C = self.transform(model.vertices[f3],translate,scale)

                normal = cross(sub(B, A), sub(C, A))
                intensity = dot(norm(normal), light)
                #print(intensity)
                #grey = round(255* intensity )
                #print(grey)
                if not texture: 
                    grey = round(255* intensity )
                    if grey < 0:
                        continue
                    intensityColor = color(grey, grey, grey)
                    self.triangle(A, B, C, intensityColor)
                else:
                    t1 = face[0][1] - 1
                    t2 = face[1][1] - 1
                    t3 = face[2][1] - 1
                    tA = V2(*model.tvertices[t1])
                    tB = V2(*model.tvertices[t2])
                    tC = V2(*model.tvertices[t3])

                    self.triangle2(A, B, C, texture=texture, texture_coords=(tA, tB, tC), intensity=intensity)

            else:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1   
                
                A = self.transform(model.vertices[f1], translate,scale)
                B = self.transform(model.vertices[f2], translate,scale)
                C = self.transform(model.vertices[f3], translate,scale)
                D = self.transform(model.vertices[f4], translate,scale)

                normal = cross(sub(B, A), sub(C, A))
                intensity = dot(norm(normal), light)
                grey = round(intensity  *255)

                if not texture:
                    grey = round(intensity  *255)
                    if grey < 0:
                        continue
                    intensityColor = color(grey, grey, grey)
                    
                    self.triangle(A, B, C, intensityColor)
                    self.triangle(A, D, C, intensityColor)
                else: 
                    t1 = face[0][1] - 1
                    t2 = face[1][1] - 1
                    t3 = face[2][1] - 1
                    t4 = face[3][1] - 1
                    tA = V3(*model.tvertices[t1])
                    tB = V3(*model.tvertices[t2])
                    tC = V3(*model.tvertices[t3])
                    tD = V3(*model.tvertices[t4])
            
                    self.triangle2(A, B, C, texture=texture, texture_coords=(tA, tB, tC), intensity=intensity)
                    self.triangle2(A, C, D, texture=texture, texture_coords=(tA, tC, tD), intensity=intensity)

    def load1(self, filename, translate, scale, texture=None):
        model = Obj(filename)
        vertex_buffer_object = []

        for face in model.faces:
            vcount = len(face)
            
            for v in range(vcount):
                print('entro al for 1 ',)
                vertex = self.transform(model.vertices[face[v][0] -1 ], translate, scale)
                vertex_buffer_object.append(vertex)

            if self.active_texture:
                for v in range(vcount):
                    print('entro al for 2 ')
                    tvertex = V2(*model.tvertices[face[v][1]-1])
                    vertex_buffer_object.append(tvertex)
            
        self.active_vertex_array = iter(vertex_buffer_object)

    def load2(self,filename, translate, scale, rotate):
        self.loadModelMatrix(translate, scale, rotate)

        model = Obj(filename)
        vertex_buffer_object = []

        for face in model.faces:
            for facepart in face:
                vertex = self.transform1(V3(*model.vertices[facepart[0]-1]))
                vertex_buffer_object.append(vertex)

            if self.active_texture:
                for facepart in face:
                    tvertex = V3(*model.tvertices[facepart[1]-1])
                    vertex_buffer_object.append(tvertex)

        self.active_vertex_array = iter(vertex_buffer_object)

    def load3(self, filename, translate=(0, 0, 0), scale=(1, 1, 1), rotate=(0, 0, 0)):
        self.loadModelMatrix(translate, scale, rotate)
        model = Obj(filename)
        vertex_buffer_object = []
    
        for face in model.faces:
            vcount = len(face) 
            if vcount == 3:
                for facepart in face:
                    vertex = self.transform1(V3(*model.vertices[facepart[0]-1]))
                    vertex_buffer_object.append(vertex)

                if self.active_texture:
                    for facepart in face:
                        tvertex = V2(*model.tvertices[facepart[1]-1])
                        vertex_buffer_object.append(tvertex)

                    for facepart in face:
                        nvertex = V3(*model.normals[facepart[2]-1])
                        vertex_buffer_object.append(nvertex)
                        

            elif vcount == 4:
                for faceindex in [0,1,2]:
                    facepart = face[faceindex]
                    vertex = self.transform1(V3(*model.vertices[facepart[0]-1]))
                    vertex_buffer_object.append(vertex)

                if self.active_texture:
                    for faceindex in range(0,3):
                        facepart = face[faceindex]
                        tvertex = V2(*model.tvertices[facepart[1]-1])
                        vertex_buffer_object.append(tvertex)

                    for faceindex in range(0,3):
                        facepart = face[faceindex]
                        nvertex = V3(*model.normals[facepart[2]-1])
                        vertex_buffer_object.append(nvertex)

                for faceindex in [3,0,2]:
                    facepart = face[faceindex]
                    vertex = self.transform1(V3(*model.vertices[facepart[0]-1]))
                    vertex_buffer_object.append(vertex)

                if self.active_texture:
                    for faceindex in [3,0,2]:
                        facepart = face[faceindex]
                        tvertex = V2(*model.tvertices[facepart[1]-1])
                        vertex_buffer_object.append(tvertex)

                    for faceindex in [3,0,2]:
                        facepart = face[faceindex]
                        nvertex = V3(*model.normals[facepart[2]-1])
                        vertex_buffer_object.append(nvertex)
                

        self.active_vertex_array = iter(vertex_buffer_object)


    def draw_arrays(self, polygon):
        if polygon == 'TRIANGLES':
            try:
                while True:
                    self.triangle4()
            except StopIteration:
                print('Modelo Listo.')
            

    def loadModelMatrix(self, translate, scale, rotate):
        
        translate = V3(*translate)
        scale = V3(*scale)
        rotate = V3(*rotate)

        translation_matrix = [
            [1, 0, 0, translate.x],
            [0, 1, 0, translate.y],
            [0, 0, 1, translate.z],
            [0, 0, 0, 1],
        ]

        a = rotate.x
        rotation_matrix_x = [
            [1, 0, 0, 0],
            [0, math.cos(a), -math.sin(a), 0],
            [0, math.sin(a),  math.cos(a), 0],
            [0, 0, 0, 1]
        ]

        a = rotate.y
        rotation_matrix_y = [
            [math.cos(a), 0,  math.sin(a), 0],
            [     0, 1,       0, 0],
            [-math.sin(a), 0,  math.cos(a), 0],
            [     0, 0,       0, 1]
        ]

        a = rotate.z
        rotation_matrix_z = [
            [math.cos(a), -math.sin(a), 0, 0],
            [math.sin(a),  math.cos(a), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]

        rotation_matrix = MM(rotation_matrix_x, rotation_matrix_y)
        rotation_matrix = MM(rotation_matrix, rotation_matrix_z)

        scale_matrix = [
            [scale.x, 0, 0, 0],
            [0, scale.y, 0, 0],
            [0, 0, scale.z, 0],
            [0, 0, 0, 1],
        ]
        
        tempM = MM(translation_matrix, rotation_matrix)
        tempM = MM(tempM, scale_matrix)
        self.Model = tempM
        
    def loadViewMatrix(self, x, y, z, center):
        Mi = [
            [x.x, x.y, x.z, 0],
            [y.x, y.y, y.z, 0],
            [z.x, z.y, z.z, 0],
            [0,0,0,1]
        ]

        Op = [
            [1, 0, 0, -center.x],
            [0, 1, 0, -center.y],
            [0, 0, 1, -center.z],
            [0, 0, 0, 1]
        ]

        self.View = MM(Mi, Op)

    def loadProjectionMatrix(self, coeff):
        self.Projection = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, coeff, 1]
        ]
    
    def loadViewportMatrix(self, x = 0, y = 0):
        self.Viewport = [
            [self.width/2, 0, 0, x + self.width/2],
            [0, self.height/2, 0, y + self.height/2],
            [0, 0, 128, 128],
            [0, 0, 0, 1]
        ]

    def lookAt(self, eye, center, up):
        z = norm(sub(eye, center))
        x = norm(cross(up, z))
        y = norm(cross(z, x))
        self.loadViewMatrix(x, y, z, center)
        self.loadProjectionMatrix(-1 / length(sub(eye, center)))
        self.loadViewportMatrix()


def gourad(render, **kwargs):
    w, v, u = kwargs['bar']
    tx, ty = kwargs['texture_coords']
    tcolor = render.active_texture.get_color(tx, ty)
    nA, nB, nC = kwargs['varying_normals']

    iA, iB, iC = [dot(n, render.light) for n in (nA, nB, nC)]
    intensity = w*iA + u*iB + v*iC
    
    return color(
        int(tcolor[2] * intensity) if tcolor[0] * intensity > 0 else 0,
        int(tcolor[1] * intensity) if tcolor[1] * intensity > 0 else 0,
        int(tcolor[0] * intensity) if tcolor[2] * intensity > 0 else 0
    )


def fragment(render, **kwargs):
    w, v, u = kwargs['bar']
    tx, ty = kwargs['texture_coords']
    grey = int(ty * 256)
    tcolor = color(grey, 150, 150)
    nA, nB, nC = kwargs['varying_normals']

    iA, iB, iC = [dot(n, render.light) for n in (nA, nB, nC)]
    intensity = w*iA + u*iB + v*iC

    if (intensity > 0.85):
        intensity = 1
    elif (intensity > 0.60):
        intensity = 0.80
    elif (intensity > 0.45):
        intensity = 0.60
    elif (intensity > 0.30):
        intensity = 0.45
    elif (intensity > 0.15):
        intensity = 0.30
    else:
        intensity = 0

    return color(
        int(tcolor[2] * intensity) if tcolor[0] * intensity > 0 else 0,
        int(tcolor[1] * intensity) if tcolor[1] * intensity > 0 else 0,
        int(tcolor[0] * intensity) if tcolor[2] * intensity > 0 else 0
    )

r = Render()
r.glCreateWindow(1000, 1000)
r.glClearcolor(1, 1, 1)
t = Texture('rsz_noche.bmp')
r.active_texture = t
r.lookAt(V3(1, 0, 5), V3(0, 0, 0), V3(0, 1, 0))

for y in range(len(t.pixels)):
    for x in range(len(t.pixels[y])):
        r.point(x, y, r.active_texture.get_color(y/1000, x/1000))

#luna
t = Texture('i7.bmp')
r.active_texture = t
r.active_shader = gourad
r.lookAt(V3(1, 0, 5), V3(0, 0, 0), V3(0, 1, 0))
r.load3('sphere.obj', V3(0, 0.4, 0), V3(0.9, 0.9, 0.9), rotate=(0, -0.5, 0))
r.draw_arrays('TRIANGLES')

#calabaza
t = Texture('pumpkin.bmp')
r.active_texture = t
r.active_shader = gourad
r.load3('pumpkin.obj', V3(0.55, -0.8, 1), V3(0.06, 0.06, 0.06), rotate=(0, -0.10, 0))
r.draw_arrays('TRIANGLES')

#arboles
t = Texture('tree-texture.bmp')
r.active_texture = t
r.active_shader = gourad

r.load3('deadtree.obj', V3(0.85, -0.85, 0), V3(0.07, 0.08, 0.06), rotate=(0, -1, 0))
r.draw_arrays('TRIANGLES')

r.load3('deadtree.obj', V3(-0.40, -0.85, 1), V3(0.065, 0.07, 0.06), rotate=(0, 0, -0.1))
r.draw_arrays('TRIANGLES')

r.load3('deadtree.obj', V3(-0.60, -0.70, 1), V3(0.066, 0.08, 0.06), rotate=(0, -1, 0))
r.draw_arrays('TRIANGLES')

#valla
r.load3('fence-wood.obj', V3(-0.1, -0.8, 1.2), V3(0.003, 0.003, 0.003), rotate=(-1, 0, 1.5)) 
r.draw_arrays('TRIANGLES')

#murcielagos
t = Texture('cuero_texture.bmp')
r.active_texture = t
r.active_shader = gourad
r.load3('bat.obj', V3(0, -0.12, 0), V3(0.04, 0.04, 0.04), rotate=(0, 0, 0))
r.draw_arrays('TRIANGLES')

r.load3('bat.obj', V3(0.65, 0.6, 0), V3(0.03, 0.03, 0.03), rotate=(0, 0, 0))
r.draw_arrays('TRIANGLES')

#tumbas
t = Texture('rip-texture2.bmp')
r.active_texture = t
r.active_shader = gourad
r.load3('rip.obj', V3(0.5, -0.85, 0), V3(0.05, 0.05, 0.05), rotate=(0, 0.8, 0))
r.draw_arrays('TRIANGLES')

t = Texture('rip-texture2.bmp')
r.active_texture = t
r.active_shader = gourad
r.load3('rip.obj', V3(-0.1, -0.85, 0), V3(0.045, 0.045, 0.045), rotate=(0, 0.5, 0))
r.draw_arrays('TRIANGLES')

#calavera
t = Texture('skull-texture.bmp')
r.active_texture = t
r.active_shader = gourad
r.load3('skull.obj', V3(-0.05, -0.8, 1), V3(0.09, 0.09, 0.09), rotate=(0, -0.5, 0))
r.draw_arrays('TRIANGLES')

r.glFinish()