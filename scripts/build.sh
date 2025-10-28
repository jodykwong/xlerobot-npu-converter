#!/bin/bash

# XLeRobot NPU Converter - Docker Build Script
# This script provides one-click Docker environment setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="xlerobot-npu-converter"
CONTAINER_NAME="xlerobot-npu-converter-dev"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        log_info "Please install Docker and try again"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        log_info "Please start Docker and try again"
        exit 1
    fi

    log_success "Docker is available and running"
}

# Check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "docker-compose is not installed"
        log_info "Please install docker-compose and try again"
        exit 1
    fi

    log_success "docker-compose is available"
}

# Build Docker image
build_image() {
    log_info "Building Docker image: $IMAGE_NAME"

    cd "$PROJECT_ROOT"

    # Build with no-cache for clean build
    if docker build --no-cache -t "$IMAGE_NAME" .; then
        log_success "Docker image built successfully"
    else
        log_error "Docker image build failed"
        exit 1
    fi
}

# Check image size
check_image_size() {
    log_info "Checking image size..."

    size_output=$(docker images "$IMAGE_NAME" --format "{{.Size}}")
    if [[ $? -eq 0 ]]; then
        log_info "Image size: $size_output"

        # Parse size and check if under 5GB
        if [[ $size_output =~ ([0-9.]+)\s*GB ]]; then
            size_gb=${BASH_REMATCH[1]}
            if (( $(echo "$size_gb < 5.0" | bc -l) )); then
                log_success "Image size is under 5GB limit"
            else
                log_warning "Image size exceeds 5GB limit: ${size_gb}GB"
            fi
        fi
    else
        log_warning "Could not determine image size"
    fi
}

# Run container and validate
validate_container() {
    log_info "Starting container for validation..."

    # Start container in background
    container_id=$(docker run -d --name "$CONTAINER_NAME" "$IMAGE_NAME" tail -f /dev/null)

    if [[ $? -ne 0 ]]; then
        log_error "Failed to start container"
        exit 1
    fi

    log_info "Container started: ${container_id:0:12}"

    # Wait for container to be ready
    sleep 3

    # Run validation tests
    log_info "Running validation tests..."

    validation_passed=true

    # Test Python version
    if docker exec "$CONTAINER_NAME" python --version | grep -q "Python 3.10"; then
        log_success "✓ Python 3.10 is available"
    else
        log_error "✗ Python 3.10 not available"
        validation_passed=false
    fi

    # Test working directory
    if [[ $(docker exec "$CONTAINER_NAME" pwd) == "/app" ]]; then
        log_success "✓ Working directory is /app"
    else
        log_error "✗ Working directory not set correctly"
        validation_passed=false
    fi

    # Test user permissions
    if [[ $(docker exec "$CONTAINER_NAME" whoami) != "root" ]]; then
        log_success "✓ Running as non-root user"
    else
        log_error "✗ Container is running as root"
        validation_passed=false
    fi

    # Test package imports
    packages=("numpy" "pyyaml" "click" "onnx" "onnxruntime")
    for package in "${packages[@]}"; do
        if docker exec "$CONTAINER_NAME" python -c "import $package" &>/dev/null; then
            log_success "✓ Package $package is importable"
        else
            log_error "✗ Package $package is not importable"
            validation_passed=false
        fi
    done

    # Cleanup
    docker stop "$CONTAINER_NAME" &>/dev/null
    docker rm "$CONTAINER_NAME" &>/dev/null

    if [[ "$validation_passed" == true ]]; then
        log_success "All validation tests passed"
        return 0
    else
        log_error "Some validation tests failed"
        return 1
    fi
}

# Show usage information
show_usage() {
    log_info "Docker environment is ready!"
    echo
    echo "Available commands:"
    echo "  docker run -it --rm $IMAGE_NAME bash                    # Start interactive shell"
    echo "  docker run --rm -v \$(pwd):/app $IMAGE_NAME python -m pytest  # Run tests"
    echo "  docker-compose up -d                                  # Start with docker-compose"
    echo "  docker-compose exec npu-converter bash                 # Enter running container"
    echo
    echo "For development with volume mounts:"
    echo "  docker run -it --rm -v \$(pwd)/src:/app/src $IMAGE_NAME bash"
    echo
}

# Main function
main() {
    echo "🚀 XLeRobot NPU Converter - Docker Build Script"
    echo "=================================================="

    # Change to project root
    cd "$PROJECT_ROOT"

    # Run checks and build
    check_docker
    check_docker_compose
    build_image
    check_image_size

    # Validate container
    if validate_container; then
        show_usage
        log_success "Docker environment setup completed successfully!"
        exit 0
    else
        log_error "Docker environment validation failed!"
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    "clean")
        log_info "Cleaning up Docker resources..."
        docker rmi "$IMAGE_NAME" 2>/dev/null || true
        docker system prune -f
        log_success "Cleanup completed"
        ;;
    "validate")
        log_info "Running validation only..."
        check_docker
        validate_container
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [clean|validate|help]"
        echo
        echo "Commands:"
        echo "  clean    - Remove Docker image and cleanup"
        echo "  validate - Run validation tests only"
        echo "  help     - Show this help message"
        echo "  (no args) - Build and validate Docker environment"
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac