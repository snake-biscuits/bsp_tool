import sys
sys.path.insert(0, '../')
import bsp_tool
import itertools


def calcTriFanIndices(face, vertices, startIndex):
	indices = []
	for i in range(1, len(vertices) - 1):
		indices += [startIndex, startIndex + i, startIndex + i + 1]
	return indices


TF = 'E:/Steam/SteamApps/common/Team Fortress 2/tf/'
bsp = '../maps/pl_upward.bsp'

bsp = bsp_tool.bsp(bsp)
print(bsp.filename.upper(), end=' ')
print(f'{bsp.bytesize // 1024:,}KB BSP', end=' >>> ')

filtered_faces = list(filter(lambda x: x['lightofs'] != -1, bsp.FACES)) #no sky or trigger
##    filtered_faces = list(filter(lambda x: x['lightofs'] != -1 and x['dispinfo'] == -1, bsp.FACES)) #no sky, trigger or disp
##    filtered_faces = list(filter(lambda x: x['styles'] == (-1, -1, -1, -1), bsp.FACES))
##    filtered_faces = bsp.FACES

face_count = len(filtered_faces)
current_face_index = 0
current_face = filtered_faces[current_face_index]
current_face_verts = [v[0] for v in bsp.verts_of(current_face)]

vertices = []
indices = []
currentIndex = 0;
for face in filtered_faces:
	if face["dispinfo"] == -1:
		faceVerts = bsp.verts_of(face)
		faceIndices = calcTriFanIndices(face, faceVerts, currentIndex)

		vertices += faceVerts
		indices += faceIndices

		currentIndex = faceIndices[len(faceIndices) - 1] + 1

