#pragma once

#include <cstring>

#include <GL/gl.h>
// #include <GL/glu.h>
#include <glm/vec3.hpp>
#include <glm/mat4x4.hpp>
#include <glm/trigonometric.hpp>
#include <glm/ext.hpp>


#include "common.hpp"


// NOTE: this camera system assumes a Z-up world

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
            glm::mat4 matrix;

        // METHODS
        void update_matrix() {  // generate a fresh perspective matrix
            matrix = glm::perspective(glm::radians(fov), aspect_ratio, clip.near, clip.far);
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
            // NOTE: uninterpolated
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

            glm::mat4 rotate(glm::mat4 in_matrix) {
                glm::mat4 out_matrix = glm::rotate(in_matrix, glm::radians(-90.0f), glm::vec3(1, 0, 0));  // Z+ up; Y+ forward
                out_matrix = glm::rotate(out_matrix, glm::radians(rotation.x), glm::vec3(1, 0, 0));
                out_matrix = glm::rotate(out_matrix, glm::radians(rotation.z), glm::vec3(0, 0, 1));
                return out_matrix;
            };

            glm::mat4 translate(glm::mat4 in_matrix) {
                return glm::translate(in_matrix, glm::vec3(-position.x, -position.y, -position.z));
            };
    };
}
