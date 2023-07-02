#version 330 core
in vec2 v_texture;
out vec4 FragColor;

uniform sampler2D textureSampler;

void main()
{    
    FragColor = texture(textureSampler, v_texture);
}