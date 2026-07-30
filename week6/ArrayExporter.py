import bpy
import bmesh

obj = bpy.context.active_object

if obj is None or obj.type != 'MESH':
    print("กรุณาเลือกวัตถุชนิด Mesh")
else:
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh = obj.data

    # สร้าง BMesh ชั่วคราวเพื่อ access face-loop และ triangulate ได้
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces)

    vertex_data = []

    for face in bm.faces:
        for vert in face.verts:
            world_coord = obj.matrix_world @ vert.co
            vertex_data.extend([
                round(world_coord.x, 4),
                round(world_coord.y, 4),
                round(world_coord.z, 4)
            ])

    bm.free()

    # แปลงเป็น JavaScript array
    js_array_str = ', '.join(map(str, vertex_data))
    js_output = f"const vertices = [\n  {js_array_str}\n];"

    # เขียนลง Text Editor
    if "ExportedJS" not in bpy.data.texts:
        bpy.data.texts.new("ExportedJS")
    bpy.data.texts["ExportedJS"].clear()
    bpy.data.texts["ExportedJS"].write(js_output)

    print("✅ Exported triangles ไปที่ TextBlock: ExportedJS แล้ว")