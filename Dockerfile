FROM ros:humble

# 기본 패키지 설치
RUN apt-get update && apt-get install -y \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-slam-toolbox \
    ros-humble-rviz2 \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher \
    ros-humble-xacro \
    # OpenGL 및 X11 관련 패키지 추가
    mesa-utils \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    x11-apps \
    x11-xserver-utils \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 생성
WORKDIR /workspace

# launch 파일 복사
COPY launch /workspace/launch
COPY config /workspace/config

# 환경 변수 설정
ENV ROS_DOMAIN_ID=0
ENV TURTLEBOT3_MODEL=waffle

# 실행 스크립트 생성
RUN echo '#!/bin/bash\n\
source /opt/ros/humble/setup.bash\n\
exec "$@"' > /entrypoint.sh && \
chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"] 