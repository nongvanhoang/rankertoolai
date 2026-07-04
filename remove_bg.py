from PIL import Image
from collections import deque

src = u"E:\\Ông Hoàng (New)\\AFF Global\\logo\\2.png"
dst = r"c:\Users\Admin\RankerToolAI\html\assets\images\logo-icon.png"

img = Image.open(src).convert("RGBA")
w, h = img.size
data = img.load()

def color_dist(c1, c2, tol=45):
    return all(abs(int(c1[i]) - int(c2[i])) <= tol for i in range(3))

seeds = [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]
bg_colors = [data[x,y] for x,y in seeds]
print("BG colors:", bg_colors)

visited = [[False]*h for _ in range(w)]
queue = deque()
for sx, sy in seeds:
    if not visited[sx][sy]:
        queue.append((sx, sy))
        visited[sx][sy] = True

while queue:
    x, y = queue.popleft()
    r, g, b, a = data[x, y]
    data[x, y] = (r, g, b, 0)
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = x+dx, y+dy
        if 0 <= nx < w and 0 <= ny < h and not visited[nx][ny]:
            px = data[nx, ny]
            if any(color_dist(px, bgc) for bgc in bg_colors):
                visited[nx][ny] = True
                queue.append((nx, ny))

img.save(dst, "PNG")
print(f"Done: {w}x{h} saved to {dst}")
