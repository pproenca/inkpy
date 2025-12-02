#!/usr/bin/env bash
# setup.sh - Interactive development setup for InkPy
# A menu-driven script to set up the development environment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Portable timeout function (works on macOS and Linux)
run_with_timeout() {
    local timeout_seconds=$1
    shift

    # Try GNU timeout first (Linux or brew install coreutils)
    if command -v timeout &> /dev/null; then
        timeout "$timeout_seconds" "$@"
        return $?
    fi

    # Try gtimeout (macOS with coreutils)
    if command -v gtimeout &> /dev/null; then
        gtimeout "$timeout_seconds" "$@"
        return $?
    fi

    # Fallback: use background process with kill
    "$@" &
    local pid=$!
    local count=0
    while kill -0 $pid 2>/dev/null && [ $count -lt $timeout_seconds ]; do
        sleep 1
        count=$((count + 1))
    done
    if kill -0 $pid 2>/dev/null; then
        kill $pid 2>/dev/null
        wait $pid 2>/dev/null
        return 124  # Same exit code as GNU timeout
    fi
    wait $pid
    return $?
}

# Status tracking
DEPS_INSTALLED=false
TESTS_PASSED=false
HOOKS_INSTALLED=false
EXAMPLES_VALIDATED=false

# ============================================================================
# Utility Functions
# ============================================================================

print_header() {
    echo -e "\n${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  $1${NC}"
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

press_enter_to_continue() {
    echo ""
    read -p "Press Enter to return to menu..."
}

# ============================================================================
# Setup Functions
# ============================================================================

check_prerequisites() {
    print_header "Checking Prerequisites"

    local all_ok=true

    # Check Python
    if command -v python3 &> /dev/null; then
        local py_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        local py_major=$(echo "$py_version" | cut -d. -f1)
        local py_minor=$(echo "$py_version" | cut -d. -f2)

        if [ "$py_major" -ge 3 ] && [ "$py_minor" -ge 9 ]; then
            print_success "Python $py_version found (>= 3.9 required)"
        else
            print_error "Python $py_version found, but >= 3.9 is required"
            all_ok=false
        fi
    else
        print_error "Python 3 not found"
        print_info "Install Python 3.9+ from https://python.org"
        all_ok=false
    fi

    # Check uv
    if command -v uv &> /dev/null; then
        local uv_version=$(uv --version 2>/dev/null | head -1)
        print_success "uv found: $uv_version"
    else
        print_warning "uv not found (recommended but optional)"
        print_info "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        print_info "Fallback: pip will be used instead"
    fi

    # Check git
    if command -v git &> /dev/null; then
        print_success "git found"
    else
        print_warning "git not found (needed for pre-commit hooks)"
    fi

    # Check if we're in the right directory
    if [ -f "pyproject.toml" ]; then
        print_success "pyproject.toml found - correct directory"
    else
        print_error "pyproject.toml not found"
        print_info "Please run this script from the inkpy project root"
        all_ok=false
    fi

    echo ""
    if [ "$all_ok" = true ]; then
        print_success "All prerequisites satisfied!"
    else
        print_error "Some prerequisites are missing"
    fi

    press_enter_to_continue
}

install_dependencies() {
    print_header "Installing Dependencies"

    if command -v uv &> /dev/null; then
        print_info "Using uv to install dependencies..."
        echo ""

        if uv sync; then
            echo ""
            print_success "Dependencies installed successfully with uv"
            DEPS_INSTALLED=true
        else
            print_error "Failed to install dependencies"
            DEPS_INSTALLED=false
        fi
    else
        print_info "uv not found, using pip fallback..."
        echo ""

        # Create venv if it doesn't exist
        if [ ! -d ".venv" ]; then
            print_info "Creating virtual environment..."
            python3 -m venv .venv
        fi

        # Activate and install
        source .venv/bin/activate

        if pip install -e ".[dev]"; then
            echo ""
            print_success "Dependencies installed successfully with pip"
            print_info "Virtual environment created at .venv/"
            print_info "Activate with: source .venv/bin/activate"
            DEPS_INSTALLED=true
        else
            print_error "Failed to install dependencies"
            DEPS_INSTALLED=false
        fi
    fi

    press_enter_to_continue
}

run_tests() {
    print_header "Running Tests"

    local test_cmd=""
    if command -v uv &> /dev/null; then
        test_cmd="uv run pytest tests/ -v"
    elif [ -d ".venv" ]; then
        test_cmd=".venv/bin/pytest tests/ -v"
    else
        print_error "No virtual environment found. Please install dependencies first."
        press_enter_to_continue
        return
    fi

    print_info "Running: $test_cmd"
    echo ""

    if $test_cmd; then
        echo ""
        print_success "All tests passed!"
        TESTS_PASSED=true
    else
        echo ""
        print_error "Some tests failed"
        TESTS_PASSED=false
    fi

    press_enter_to_continue
}

install_precommit_hooks() {
    print_header "Installing Pre-commit Hooks"

    local precommit_cmd=""
    if command -v uv &> /dev/null; then
        precommit_cmd="uv run pre-commit"
    elif [ -d ".venv" ]; then
        precommit_cmd=".venv/bin/pre-commit"
    else
        print_error "No virtual environment found. Please install dependencies first."
        press_enter_to_continue
        return
    fi

    if ! command -v git &> /dev/null; then
        print_error "git is required for pre-commit hooks"
        press_enter_to_continue
        return
    fi

    print_info "Installing git hooks..."
    echo ""

    if $precommit_cmd install; then
        echo ""
        print_success "Pre-commit hooks installed!"
        print_info "Hooks will run automatically on git commit"
        HOOKS_INSTALLED=true
    else
        print_error "Failed to install pre-commit hooks"
        HOOKS_INSTALLED=false
    fi

    press_enter_to_continue
}

validate_examples() {
    print_header "Validating Examples"

    local run_cmd=""
    if command -v uv &> /dev/null; then
        run_cmd="uv run python"
    elif [ -d ".venv" ]; then
        run_cmd=".venv/bin/python"
    else
        print_error "No virtual environment found. Please install dependencies first."
        press_enter_to_continue
        return
    fi

    local examples_ok=true

    # Test hello_world.py
    print_info "Testing examples/hello_world.py..."
    if run_with_timeout 5 $run_cmd examples/hello_world.py &> /dev/null; then
        print_success "hello_world.py runs successfully"
    else
        print_error "hello_world.py failed"
        examples_ok=false
    fi

    # Test counter.py (with timeout since it's interactive)
    print_info "Testing examples/counter.py (quick validation)..."
    if run_with_timeout 2 $run_cmd -c "
import sys
sys.path.insert(0, '.')
from examples.counter import Counter
print('Counter component imports successfully')
" 2>/dev/null; then
        print_success "counter.py imports successfully"
    else
        print_error "counter.py import failed"
        examples_ok=false
    fi

    echo ""
    if [ "$examples_ok" = true ]; then
        print_success "All examples validated!"
        EXAMPLES_VALIDATED=true
    else
        print_error "Some examples failed validation"
        EXAMPLES_VALIDATED=false
    fi

    press_enter_to_continue
}

full_setup() {
    print_header "Full Setup"
    print_info "This will run all setup steps in sequence"
    echo ""

    # Check prerequisites
    echo -e "${BOLD}Step 1/4: Checking prerequisites...${NC}"
    check_prerequisites_silent

    # Install dependencies
    echo -e "\n${BOLD}Step 2/4: Installing dependencies...${NC}"
    install_dependencies_silent

    # Run tests
    echo -e "\n${BOLD}Step 3/4: Running tests...${NC}"
    run_tests_silent

    # Validate examples
    echo -e "\n${BOLD}Step 4/4: Validating examples...${NC}"
    validate_examples_silent

    # Summary
    echo ""
    print_header "Setup Complete!"

    echo -e "  Dependencies:  $(status_icon $DEPS_INSTALLED)"
    echo -e "  Tests:         $(status_icon $TESTS_PASSED)"
    echo -e "  Examples:      $(status_icon $EXAMPLES_VALIDATED)"
    echo ""

    if [ "$DEPS_INSTALLED" = true ] && [ "$TESTS_PASSED" = true ]; then
        print_success "InkPy is ready for development!"
        echo ""
        print_info "Quick commands:"
        echo "  uv run pytest          # Run tests"
        echo "  uv run ruff check .    # Lint code"
        echo "  uv run mypy inkpy/     # Type check"
        echo "  python examples/hello_world.py  # Run example"
    else
        print_warning "Setup completed with some issues. Check the status above."
    fi

    press_enter_to_continue
}

# Silent versions for full setup (no pause)
check_prerequisites_silent() {
    if command -v python3 &> /dev/null; then
        local py_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        print_success "Python $py_version"
    else
        print_error "Python not found"
    fi

    if command -v uv &> /dev/null; then
        print_success "uv available"
    else
        print_warning "uv not found (will use pip)"
    fi
}

install_dependencies_silent() {
    if command -v uv &> /dev/null; then
        if uv sync 2>&1 | tail -5; then
            print_success "Dependencies installed"
            DEPS_INSTALLED=true
        else
            print_error "Dependency installation failed"
        fi
    else
        if pip install -e ".[dev]" 2>&1 | tail -5; then
            print_success "Dependencies installed"
            DEPS_INSTALLED=true
        else
            print_error "Dependency installation failed"
        fi
    fi
}

run_tests_silent() {
    local test_cmd=""
    if command -v uv &> /dev/null; then
        test_cmd="uv run pytest tests/ -q"
    elif [ -d ".venv" ]; then
        test_cmd=".venv/bin/pytest tests/ -q"
    fi

    if $test_cmd 2>&1 | tail -10; then
        TESTS_PASSED=true
    else
        TESTS_PASSED=false
    fi
}

validate_examples_silent() {
    local run_cmd=""
    if command -v uv &> /dev/null; then
        run_cmd="uv run python"
    elif [ -d ".venv" ]; then
        run_cmd=".venv/bin/python"
    fi

    if run_with_timeout 5 $run_cmd examples/hello_world.py &> /dev/null; then
        print_success "Examples validated"
        EXAMPLES_VALIDATED=true
    else
        print_error "Example validation failed"
        EXAMPLES_VALIDATED=false
    fi
}

status_icon() {
    if [ "$1" = true ]; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
    fi
}

# ============================================================================
# Menu
# ============================================================================

show_menu() {
    clear
    echo -e "${BOLD}${CYAN}"
    echo "  ╔═══════════════════════════════════════════════════════════════╗"
    echo "  ║                                                               ║"
    echo "  ║   ██╗███╗   ██╗██╗  ██╗██████╗ ██╗   ██╗                      ║"
    echo "  ║   ██║████╗  ██║██║ ██╔╝██╔══██╗╚██╗ ██╔╝                      ║"
    echo "  ║   ██║██╔██╗ ██║█████╔╝ ██████╔╝ ╚████╔╝                       ║"
    echo "  ║   ██║██║╚██╗██║██╔═██╗ ██╔═══╝   ╚██╔╝                        ║"
    echo "  ║   ██║██║ ╚████║██║  ██╗██║        ██║                         ║"
    echo "  ║   ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝        ╚═╝                         ║"
    echo "  ║                                                               ║"
    echo "  ║              Development Environment Setup                    ║"
    echo "  ║                                                               ║"
    echo "  ╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    echo -e "  ${BOLD}Current Status:${NC}"
    echo -e "    Dependencies: $([ "$DEPS_INSTALLED" = true ] && echo -e "${GREEN}Installed${NC}" || echo -e "${YELLOW}Not installed${NC}")"
    echo -e "    Tests:        $([ "$TESTS_PASSED" = true ] && echo -e "${GREEN}Passing${NC}" || echo -e "${YELLOW}Not run${NC}")"
    echo -e "    Pre-commit:   $([ "$HOOKS_INSTALLED" = true ] && echo -e "${GREEN}Installed${NC}" || echo -e "${YELLOW}Not installed${NC}")"
    echo -e "    Examples:     $([ "$EXAMPLES_VALIDATED" = true ] && echo -e "${GREEN}Validated${NC}" || echo -e "${YELLOW}Not validated${NC}")"
    echo ""

    echo -e "  ${BOLD}Menu:${NC}"
    echo -e "    ${CYAN}1${NC}) Full Setup (recommended for first-time setup)"
    echo -e "    ${CYAN}2${NC}) Install Dependencies"
    echo -e "    ${CYAN}3${NC}) Run Tests"
    echo -e "    ${CYAN}4${NC}) Install Pre-commit Hooks"
    echo -e "    ${CYAN}5${NC}) Validate Examples"
    echo -e "    ${CYAN}6${NC}) Check Prerequisites"
    echo -e "    ${CYAN}q${NC}) Exit"
    echo ""
}

# ============================================================================
# Main
# ============================================================================

main() {
    # Check if we're in the right directory
    if [ ! -f "pyproject.toml" ]; then
        echo -e "${RED}Error: pyproject.toml not found${NC}"
        echo "Please run this script from the inkpy project root directory."
        exit 1
    fi

    while true; do
        show_menu
        read -p "  Select an option: " choice

        case $choice in
            1) full_setup ;;
            2) install_dependencies ;;
            3) run_tests ;;
            4) install_precommit_hooks ;;
            5) validate_examples ;;
            6) check_prerequisites ;;
            q|Q)
                echo ""
                print_info "Goodbye! Happy coding with InkPy!"
                echo ""
                exit 0
                ;;
            *)
                print_error "Invalid option"
                sleep 1
                ;;
        esac
    done
}

# Run main
main "$@"
