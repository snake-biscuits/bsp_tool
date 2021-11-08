#pragma once

#include <cmath>


#ifndef M_PI
    #define M_PI 3.14159265358979323846
#endif
#define RADIANS(degrees)  degrees * M_PI / 180


class Vector {
    public:
        float  x, y, z;

        // OPERATORS
        Vector operator+(const Vector& other) {
            static Vector out;
            out.x = x + other.x;
            out.y = y + other.y;
            out.z = z + other.z;
            return out;
        }

        Vector& operator+=(const Vector& other) {
            this->x = x + other.x;
            this->y = y + other.y;
            this->z = z + other.z;
            return *this;
        }

        Vector& operator-() {  // __neg__
            static Vector out;
            out.x = -x;
            out.y = -y;
            out.z = -z;
            return out;
        }

        Vector& operator-(const Vector& other) {
            static Vector out;
            out.x = x - other.x;
            out.y = y - other.y;
            out.z = z - other.z;
            return out;
        }

        Vector& operator-=(const Vector& other) {
            this->x = x - other.x;
            this->y = y - other.y;
            this->z = z - other.z;
            return *this;
        }

        Vector operator*(const float& scalar) {
            static Vector out;
            out.x = x * scalar;
            out.y = y * scalar;
            out.z = z * scalar;
            return out;
        }

        Vector& operator*=(const float& scalar) {
            this->x = x * scalar;
            this->y = y * scalar;
            this->z = z * scalar;
            return *this;
        }

        // METHODS
        Vector rotate(Vector angle) {
            static Vector out;
            // ROTATE X
            float cos_x = cos(RADIANS(angle.x));
            float sin_x = sin(RADIANS(angle.x));
            Vector temp;
            out.y = y * cos_x - z * sin_x;
            out.z = y * sin_x + z * cos_x;
            // ROTATE Y
            float cos_y = cos(RADIANS(angle.y));
            float sin_y = sin(RADIANS(angle.y));
            temp = {out.x, out.y, out.z};
            out.x = x * cos_y + temp.z * sin_y;
            out.z = x * sin_y + temp.z * cos_y;
            // ROTATE Z
            float cos_z = cos(RADIANS(angle.z));
            float sin_z = sin(RADIANS(angle.z));
            temp = {out.x, out.y, out.z};
            out.x = temp.x * cos_z - temp.y * sin_z;
            out.y = temp.x * sin_z + temp.y * cos_z;
            return out;
        }
};

class Vector2D {
    public:
        float  x, y;

        // OPERATORS
        Vector2D operator+(const Vector2D& other) {
            static Vector2D out;
            out.x = x + other.x;
            out.y = y + other.y;
            return out;
        }

        Vector2D& operator+=(const Vector2D& other) {
            this->x = x + other.x;
            this->y = y + other.y;
            return *this;
        }

        Vector2D operator*(const float& scalar) {
            static Vector2D out;
            out.x = x * scalar;
            out.y = y * scalar;
            return out;
        }

        Vector2D& operator*=(const float& scalar) {
            this->x = x * scalar;
            this->y = y * scalar;
            return *this;
        }

        // METHODS
        Vector rotate(float degrees) {
            static Vector out;
            float cos_theta = cos(RADIANS(degrees));
            float sin_theta = sin(RADIANS(degrees));
            out.x = x * cos_theta + y * sin_theta;
            out.y = y * cos_theta - x * sin_theta;
            return out;
        }
};

struct QAngle { float pitch, yaw, roll; };  // Y Z X; 0 0 0 = Facing East / X+;

struct Colour32 { unsigned char r, g, b, a; };
