#Codigo ayuda: https://github.com/churly92/Engine3D/blob/main/gl.py
#Repositorio perteneciente a Prof. Carlos Alonso

#Mirka Monzon 18139
#Proyecto 1: Software Renderer


from gl import V3, color, dot


def myshader(**kwargs):
  texture_color = kwargs['texture_color']
  w, u, v =kwargs['barycentric_coords']
  nA, nB, nC = kwargs['vertex_normals']
  tx, ty = kwargs['texture_coords']

  grey = int(ty * 256)
  iA, iB, iC = [dot(n, V3(0,0,1)) for n in (nA,nB,nC)]

  intensity = iA * w + iB * v + iC * u
  if intensity > 0.85:
    intensity =1
  elif intensity > 0.60:
    intensity =  0.80
  elif intensity >0.45:
    intensity = 0.5
  elif intensity >0.3:
    intensity = 0.3
  elif intensity >0.15:
    intensity = 0.1
  else:
    intensity = 0 
    r = int(texture_color[2]* intensity)
    g = int(texture_color[1]* intensity)
    b = int(texture_color[0]* intensity)

    return color(
      (r if r < 255 else 255) if r > 0 else 0,
      (g if g < 255 else 255) if g > 0 else 0,
      (b if b < 255 else 255) if b > 0 else 0,
    )

  return color(200, 0, 0)