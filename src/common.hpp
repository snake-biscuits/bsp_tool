#pragma once

#include <cmath>
#include <cstdint>


#ifndef M_PI
    #define M_PI 3.14159265358979323846
#endif
#define RADIANS(degrees)  (degrees * M_PI / 180)


template <typename T>
class Vector3D {
    public:
        T  x, y, z;

        // OPERATORS
        // NOTE: Left-hand side type takes precedence
        template<typename OT>
        Vector3D<T> operator+(const Vector3D<OT>& other) {
            static Vector3D<T> out;
            out.x = x + other.x;
            out.y = y + other.y;
            out.z = z + other.z;
            return out;
        }

        template<typename OT>
        Vector3D<T>& operator+=(const Vector3D<OT>& other) {
            this->x = x + other.x;
            this->y = y + other.y;
            this->z = z + other.z;
            return *this;
        }

        Vector3D<T>& operator-() {  // unary
            static Vector3D<T> out;
            out.x = -x;
            out.y = -y;
            out.z = -z;
            return out;
        }

        template<typename OT>
        Vector3D<T>& operator-(const Vector3D<OT>& other) {
            static Vector3D<T> out;
            out.x = x - other.x;
            out.y = y - other.y;
            out.z = z - other.z;
            return out;
        }

        template<typename OT>
        Vector3D<T>& operator-=(const Vector3D<OT>& other) {
            this->x = x - other.x;
            this->y = y - other.y;
            this->z = z - other.z;
            return *this;
        }

        template<typename ST>
        Vector3D<T> operator*(const ST& scalar) {
            static Vector3D<T> out;
            out.x = x * scalar;
            out.y = y * scalar;
            out.z = z * scalar;
            return out;
        }

        template<typename ST>
        Vector3D<T>& operator*=(const ST& scalar) {
            this->x = x * scalar;
            this->y = y * scalar;
            this->z = z * scalar;
            return *this;
        }

        // METHODS
        Vector3D<float> rotate(Vector3D<T> angle) {
            static Vector3D<float> out;
            // ROTATE X
            float cos_x = cos(RADIANS(angle.x));
            float sin_x = sin(RADIANS(angle.x));
            Vector3D<T> temp;
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


template<typename T>
class Vector2D {
    public:
        T  x, y;

        // OPERATORS
        // NOTE: Left-hand side type takes precedence
        template<typename OT>
        Vector2D<T> operator+(const Vector2D<OT>& other) {
            static Vector2D<T> out;
            out.x = x + other.x;
            out.y = y + other.y;
            return out;
        }

        template<typename OT>
        Vector2D<T>& operator+=(const Vector2D<OT>& other) {
            this->x = x + other.x;
            this->y = y + other.y;
            return *this;
        }

        template<typename ST>
        Vector2D<T> operator*(const ST& scalar) {
            static Vector2D<T> out;
            out.x = x * scalar;
            out.y = y * scalar;
            return out;
        }

        template<typename ST>
        Vector2D<T>& operator*=(const ST& scalar) {
            this->x = x * scalar;
            this->y = y * scalar;
            return *this;
        }

        // METHODS
        template<typename DT>
        Vector2D<T> rotate(DT degrees) {
            static Vector2D<T> out;
            float cos_theta = cos(RADIANS(degrees));
            float sin_theta = sin(RADIANS(degrees));
            out.x = x * cos_theta + y * sin_theta;
            out.y = y * cos_theta - x * sin_theta;
            return out;
        }
};

struct QAngle { float pitch, yaw, roll; };  // Y Z X; 0 0 0 = Facing East / X+;

struct Colour32 { uint8_t r, g, b, a; };
