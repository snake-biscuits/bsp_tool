#pragma once

#include <cstring>

#include <GL/gl.h>
#include <GL/glu.h>

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

        // METHODS
        void use() {
            // gluPerspective(fov, aspect_ratio, clip.near, clip.far);
            float fov_fraction  = 1.0f / tanf(fov * 0.5f);
            float clip_fraction = 1.0f / (clip.near - clip.far);
            GLfloat mat4[16];
            memset(mat4, 0, sizeof(mat4));
            mat4[4 * 0 + 0] = fov_fraction / aspect_ratio;
            mat4[4 * 1 + 1] = fov_fraction;
            mat4[4 * 2 + 2] = (clip.near + clip.far) * clip_fraction;
            mat4[4 * 2 + 3] = -1.0f;
            mat4[4 * 3 + 2] = 2.0f * clip.near * clip.far * clip_fraction;
            glLoadMatrixf(mat4);  // NOTE: could return instead for shaders
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
                position += wish.rotate(rotation) * speed * delta_time_ms;
            };

            void rotate() {
                glRotatef(-90, 1, 0, 0);  // Z+ UP; Y+ FRONT
                glRotatef(rotation.x, 1, 0, 0);
                glRotatef(rotation.z, 0, 0, 1);
            };

            void translate() {
                glTranslated(-position.x, -position.y, -position.z);
            };
    };
}
