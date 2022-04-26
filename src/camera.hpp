#pragma once

#include <cstring>

#include <GL/gl.h>
#include <GL/glu.h>
// TODO: glm

#include "common.hpp"


namespace camera {
    namespace MOVE {
        const int PAN_UP    = 0;  // Z+
        const int PAN_DOWN  = 1;  // Z-
        const int PAN_LEFT  = 2;  // X-
        const int PAN_RIGHT = 3;  // X+
        const int DOLLY_IN  = 4;  // Y+
        const int DOLLY_OUT = 5;  // Y-
    }


    class Lens {
        public:
            float fov;  // along Y axis
            float aspect_ratio;  // width / height
            struct {
                float near;
                float far;
            } clip;
            GLfloat matrix[4][4];

        // METHODS
        void update() {  // generate a fresh perspective matrix
            float fov_fraction  = 1.0f / tanf(fov * 0.5f);
            float clip_fraction = 1.0f / (clip.near - clip.far);
            memset(matrix, 0, sizeof(GLfloat) * 4 * 4);
            matrix[0][0] = fov_fraction / aspect_ratio;
            matrix[1][1] = fov_fraction;
            matrix[2][2] = (clip.near + clip.far) * clip_fraction;
            matrix[2][3] = -1.0f;
            matrix[3][2] = 2.0f * clip.near * clip.far * clip_fraction;
        }
    };


    class FirstPerson {
        public:
            bool    motion[6];
            Vector  position;
            Vector  rotation;
            float   sensitivity;
            float   speed;

            // METHODS
            // NOTE: no blending between ticks
            void update(Vector2D mouse, uint64_t delta_time_ms) {
                // controls break sometimes? gimball lock?
                rotation.z += mouse.x * sensitivity;
                rotation.x += mouse.y * sensitivity;
                rotation.x = rotation.x > 90 ? 90 : rotation.x < -90 ? -90 : rotation.x;
                using namespace MOVE;
                Vector wish;
                wish.x = -(motion[PAN_LEFT] - motion[PAN_RIGHT]);
                wish.y = -(motion[DOLLY_OUT] - motion[DOLLY_IN]);
                wish.z = -(motion[PAN_DOWN] - motion[PAN_UP]);
                // TODO: rotate wish with a quaternion
                position += wish.rotate(-rotation) * speed * delta_time_ms;
            };

            // TODO: use glm to rotate a given matrix
            void rotate() {
                glRotatef(-90, 1, 0, 0);  // Z+ UP; Y+ FRONT
                glRotatef(rotation.x, 1, 0, 0);
                glRotatef(rotation.z, 0, 0, 1);
            };

            // TODO: use glm to translate a given matrix
            void translate() {
                glTranslated(-position.x, -position.y, -position.z);
            };
    };
}
