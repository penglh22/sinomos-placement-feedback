#include <cstdio>
#include <cstdlib>
#include <string>
#include <iostream>


double run_python(const std::string& exe,
                  const std::string& input_file)
{
    std::string cmd = exe + " " + input_file;
    FILE* pipe = popen(cmd.c_str(), "r");
    if (!pipe) {
        throw std::runtime_error("popen failed");
    }

    char buf[256];
    if (!fgets(buf, sizeof(buf), pipe)) {
        pclose(pipe);
        throw std::runtime_error("no output");
    }

    pclose(pipe);
    return std::stod(buf);
}


int main() {
    try {
        double r = run_python(
            "./dist/main_enhanced",   // onefile 可执行路径
            "sample.bsd"
        );
        std::cout << "Result = " << r << std::endl;
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
    }
}