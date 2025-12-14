#!/usr/bin/env python3
import re


def extract_all_cells_and_pins(lib_content):
    """
    直接提取所有cell和pin信息的方法
    """
    cells = {}

    # 查找所有cell定义
    cell_pattern = r"cell\s*\(\s*(\w+)\s*\)\s*\{"
    cell_matches = list(re.finditer(cell_pattern, lib_content))

    print(f"找到 {len(cell_matches)} 个cell定义")

    for i, match in enumerate(cell_matches):
        cell_name = match.group(1)
        print(f"\n处理cell {i + 1}: {cell_name}")

        # 找到cell内容的结束位置
        cell_start = match.end()
        brace_count = 1
        cell_end = cell_start

        while cell_end < len(lib_content) and brace_count > 0:
            if lib_content[cell_end] == "{":
                brace_count += 1
            elif lib_content[cell_end] == "}":
                brace_count -= 1
            cell_end += 1

        if brace_count == 0:
            cell_content = lib_content[cell_start : cell_end - 1]
            cell_info = parse_cell_direct(cell_name, cell_content)
            cells[cell_name] = cell_info
        else:
            print(f"警告: 无法找到cell '{cell_name}' 的完整内容")

    return cells


def parse_cell_direct(cell_name, cell_content):
    """
    直接解析cell内容
    """
    cell_info = {
        "name": cell_name,
        "type": "combinational",
        "pins": {},
        "functions": {},
    }

    # 检查是否是时序单元
    if "ff (" in cell_content:
        cell_info["type"] = "sequential"
        # 提取FF信息
        ff_match = re.search(
            r'ff\s*\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)\s*\{([^}]+)\}', cell_content
        )
        if ff_match:
            cell_info["ff"] = {
                "q_pin": ff_match.group(1),
                "qn_pin": ff_match.group(2),
                "definition": ff_match.group(3),
            }
            # 提取FF属性
            for attr in ["next_state", "clocked_on", "clear"]:
                attr_match = re.search(rf'{attr}\s*:\s*"([^"]+)"', ff_match.group(3))
                if attr_match:
                    cell_info["ff"][attr] = attr_match.group(1)

    # 直接搜索所有pin定义
    pin_pattern = r"pin\s*\(\s*(\w+)\s*\)\s*\{"
    pin_matches = list(re.finditer(pin_pattern, cell_content))

    print(f"  找到 {len(pin_matches)} 个pin定义")

    for pin_match in pin_matches:
        pin_name = pin_match.group(1)
        pin_start = pin_match.end()

        # 找到pin内容的结束
        brace_count = 1
        pin_end = pin_start

        while pin_end < len(cell_content) and brace_count > 0:
            if cell_content[pin_end] == "{":
                brace_count += 1
            elif cell_content[pin_end] == "}":
                brace_count -= 1
            pin_end += 1

        if brace_count == 0:
            pin_content = cell_content[pin_start : pin_end - 1]
            pin_info = parse_pin_direct(pin_content)
            cell_info["pins"][pin_name] = pin_info

            # 如果这个pin有function，记录下来
            if "function" in pin_info:
                cell_info["functions"][pin_name] = pin_info["function"]

    # 如果没有任何pin被解析，尝试备用方法
    if not cell_info["pins"]:
        cell_info = parse_cell_fallback(cell_name, cell_content, cell_info)

    return cell_info


def parse_pin_direct(pin_content):
    """
    直接解析pin内容
    """
    pin_info = {}

    # 提取direction
    direction_match = re.search(r"direction\s*:\s*(\w+)", pin_content)
    if direction_match:
        pin_info["direction"] = direction_match.group(1)

    # 提取function - 使用更宽松的正则表达式
    function_match = re.search(r'function\s*:\s*"([^"]*)"', pin_content)
    if function_match:
        pin_info["function"] = function_match.group(1)

    # 检查是否是时钟
    if "clock" in pin_content and "true" in pin_content:
        pin_info["clock"] = True

    # 提取capacitance
    capacitance_match = re.search(r"capacitance\s*:\s*([\d.]+)", pin_content)
    if capacitance_match:
        pin_info["capacitance"] = float(capacitance_match.group(1))

    return pin_info


def parse_cell_fallback(cell_name, cell_content, cell_info):
    """
    备用解析方法：直接搜索function定义
    """
    print(f"  使用备用方法解析 {cell_name}")

    # 直接搜索function定义
    function_matches = re.findall(r'function\s*:\s*"([^"]+)"', cell_content)
    if function_matches:
        print(f"    找到function: {function_matches}")
        cell_info["direct_functions"] = function_matches

    # 搜索pin名称和方向
    pin_direction_matches = re.findall(
        r"pin\s*\(\s*(\w+)\s*\)[^{]*direction\s*:\s*(\w+)", cell_content
    )
    if pin_direction_matches:
        print(f"    找到pin方向: {pin_direction_matches}")
        for pin_name, direction in pin_direction_matches:
            cell_info["pins"][pin_name] = {"direction": direction}

    return cell_info


def generate_final_report(cells):
    """
    生成最终报告
    """
    print("\n" + "=" * 80)
    print("FINAL CELL LOGIC REPORT")
    print("=" * 80)

    for cell_name, cell_info in cells.items():
        print(f"\nCELL: {cell_name}")
        print(f"TYPE: {cell_info['type'].upper()}")
        print("-" * 40)

        if cell_info["type"] == "sequential" and "ff" in cell_info:
            ff = cell_info["ff"]
            print("FLIP-FLOP DEFINITION:")
            print(f"  Q Pin: {ff.get('q_pin', 'N/A')}")
            print(f"  QN Pin: {ff.get('qn_pin', 'N/A')}")
            print(f"  Next State: {ff.get('next_state', 'N/A')}")
            print(f"  Clocked On: {ff.get('clocked_on', 'N/A')}")
            print(f"  Clear: {ff.get('clear', 'N/A')}")

        if cell_info["pins"]:
            print("PINS:")
            for pin_name, pin_info in cell_info["pins"].items():
                direction = pin_info.get("direction", "N/A")
                function = pin_info.get("function", "N/A")
                clock = " [CLOCK]" if pin_info.get("clock") else ""
                capacitance = (
                    f" [Cap: {pin_info['capacitance']}]"
                    if "capacitance" in pin_info
                    else ""
                )
                print(f"  {pin_name}: {direction}{clock}{capacitance}")
                if function != "N/A":
                    print(f"    Function: {function}")

        if "direct_functions" in cell_info:
            print("DIRECT FUNCTIONS:")
            for func in cell_info["direct_functions"]:
                print(f"  {func}")

        if "functions" in cell_info and cell_info["functions"]:
            print("OUTPUT FUNCTIONS:")
            for pin_name, function in cell_info["functions"].items():
                print(f"  {pin_name}: {function}")

        # 推断逻辑功能
        logic_function = infer_logic_function(cell_name, cell_info)
        if logic_function:
            print(f"INFERRED LOGIC: {logic_function}")


def infer_logic_function(cell_name, cell_info):
    """
    根据cell信息推断逻辑功能
    """
    if cell_info["type"] == "sequential":
        if "ff" in cell_info:
            ff = cell_info["ff"]
            if ff.get("clocked_on") and ff.get("next_state"):
                reset_info = (
                    f" with reset ({ff.get('clear', 'none')})"
                    if ff.get("clear")
                    else ""
                )
                return f"D Flip-Flop{reset_info}: Q(t+1) = {ff['next_state']} on {ff['clocked_on']} rising edge"

    elif cell_info["type"] == "combinational":
        # 检查已知的组合逻辑单元
        if "OR2" in cell_name:
            return "2-input OR Gate: Z = A | B"
        elif "XOR2" in cell_name:
            return "2-input XOR Gate: Z = A ^ B"
        elif "AND2" in cell_name:
            return "2-input AND Gate: Z = A & B"
        elif "INV" in cell_name:
            return "Inverter: Z = !A"
        elif "NAND2" in cell_name:
            return "2-input NAND Gate: Z = !(A & B)"
        elif "NOR2" in cell_name:
            return "2-input NOR Gate: Z = !(A | B)"

        # 根据function推断
        if "functions" in cell_info and cell_info["functions"]:
            for pin_name, function in cell_info["functions"].items():
                if "|" in function:
                    return f"OR-type function: {function}"
                elif "&" in function:
                    return f"AND-type function: {function}"
                elif "^" in function:
                    return f"XOR-type function: {function}"
                elif "!" in function or "~" in function:
                    return f"Inverter-type function: {function}"

    return None


# 读取文件内容
with open("smic_cmoslib.txt", "r", encoding="utf-8") as f:
    lib_content = f.read()

print("文件读取成功，长度:", len(lib_content))

# 提取所有cell和pin信息
cells = extract_all_cells_and_pins(lib_content)

# 生成最终报告
generate_final_report(cells)

# 输出统计信息
print("\n" + "=" * 80)
print("SUMMARY:")
print(f"Total Cells: {len(cells)}")
sequential_count = sum(1 for cell in cells.values() if cell["type"] == "sequential")
combinational_count = len(cells) - sequential_count
print(f"Sequential Cells: {sequential_count}")
print(f"Combinational Cells: {combinational_count}")
print("=" * 80)
