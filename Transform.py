import math


class Transform:

    def transfunc(self, pitch, roll, yaw, x, y, z):
        if x == -1 and y == -1 and z == -1:
            # print("no values")
            return -x, -y, -z

        x_rel = x
        y_rel = -z
        z_rel = -y
        pitch_rel = -pitch
        roll_rel = roll
        yaw_rel = yaw

        # print("x_rel: ", x_rel)
        # print("y_rel: ", y_rel)
        # print("z_rel: ", z_rel)

        # Quadrant - Y
        if x_rel > 0 and z_rel > 0:
            quad_y = 0
        elif z_rel < 0 < x_rel or x_rel < 0 and z_rel < 0:
            quad_y = 180
        else:
            quad_y = 360


        # Y
        ry = (x_rel**2 + z_rel**2)**0.5
        delta_y = math.degrees(math.atan((x_rel/z_rel))) + quad_y
        zy = ry * math.cos(math.radians(delta_y-yaw_rel))
        xy = ry * math.sin(math.radians(delta_y-yaw_rel))
        yy = y_rel

        # print("ry: ", ry)
        # print("delta y: ", delta_y)
        # print("zy: ", zy)
        # print("xy: ", xy)
        # print("yy: ", yy)
        # print("Quadrant: ", quad_y)

        # Quadrant - X
        if zy > 0 and yy > 0:
            quad_x = 0
        elif yy < 0 < zy or yy < 0 and zy < 0:
            quad_x = 180
        else:
            quad_x = 360

        # X
        rx = (zy ** 2 + yy ** 2) ** 0.5
        delta_x = math.degrees(math.atan((zy / yy))) + quad_x
        yx = rx * math.cos(math.radians(delta_x - pitch_rel))
        zx = rx * math.sin(math.radians(delta_x - pitch_rel))
        xx = xy

        # print("rx: ", rx)
        # print("delta x: ", delta_x)
        # print("zx: ", zx)
        # print("xx: ", xx)
        # print("yx: ", yx)
        # print("Quadrant: ", quad_x)

        # Quadrant - Z
        if xx > 0 and yx > 0:
            quad_z = 0
        elif xx < 0 < yx or xx < 0 and yx < 0:
            quad_z = 180
        else:
            quad_z = 360
        # Z
        rz = (xx ** 2 + yx ** 2) ** 0.5
        delta_z = math.degrees(math.atan((yx / xx))) + quad_z
        xz = rz * math.cos(math.radians(delta_z - roll_rel))
        yz = rz * math.sin(math.radians(delta_z - roll_rel))
        zz = zx

        # print("rz: ", rz)
        # print("delta z: ", delta_z)
        # print("zz: ", zz)
        # print("xz: ", xz)
        # print("yz: ", yz)
        # print("Quadrant: ", quad_z)

        x_ = xz
        y_ = zz
        z_ = -yz
        return x_, y_, z_


# Testing

# transform = Transform()
# print(transform.transfunc(-26,-32,5,-31,7,96))
# print(transform.transfunc(-31,-17,-95, 16, 3, 100))

