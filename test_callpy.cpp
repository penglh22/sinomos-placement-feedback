#include <cstdio>
#include <cstdlib>
#include <string>
#include <iostream>
#include <stdexcept>

double run_python(const std::string& exe,
                  const std::string& input_file)
{
    std::string cmd = exe + " " + input_file + " 2>&1";

    std::cerr << "[C++] About to call popen(): " << cmd << std::endl;

    FILE* pipe = popen(cmd.c_str(), "r");
    if (!pipe) {
        throw std::runtime_error("popen failed");
    }

    std::cerr << "[C++] popen() returned, waiting for output..." << std::endl;

    char buf[512] = {0};
    if (!fgets(buf, sizeof(buf), pipe)) {
        pclose(pipe);
        throw std::runtime_error("no output from python");
    }

    std::cerr << "[C++] Received first line:\n" << buf;

    pclose(pipe);

    std::cerr << "[C++] popen closed, parsing result..." << std::endl;

    return std::stod(buf);
}

int main()
{
    try {
        std::cerr << "[C++] Program start" << std::endl;

        double r = run_python(
            "./dist/main_enhanced",   
            "sample.bsd"
        );

        std::cout << "Result = " << r << std::endl;
    }
    catch (const std::exception& e) {
        std::cerr << "[C++] Exception: " << e.what() << std::endl;
    }
}
