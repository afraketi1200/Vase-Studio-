import streamlit as st
import numpy as np
import trimesh
import plotly.graph_objects as go

st.set_page_config(page_title="Parametric Vase Studio Pro", layout="wide")

lang = st.radio("Language / زبان", ["Persian", "English"], horizontal=True)

TXT = {
    "title": {"Persian": "🏺 استودیو حرفه‌ای طراحی پارامتری گلدان", "English": "🏺 Parametric Vase Studio Pro"},
    "subtitle": {"Persian": "طراحی پارامتری با کف ۱۰۰٪ مسطح و صلب، ابزار برش صفحات (Plane Cut)، زوم روان و خروجی STL/STEP", "English": "Full parametric vase design with guaranteed flat solid base, plane cut, smooth zoom, and STL/STEP exports."},
    
    "exp_geometry": {"Persian": "📏 ۱. ابعاد و هندسه اصلی", "English": "📏 1. Geometry & Dimensions"},
    "exp_cut": {"Persian": "✂️ ۲. تنظیمات برش (Plane Cut)", "English": "✂️ 2. Plane Cut Settings"},
    "exp_material": {"Persian": "🎨 ۳. متریال و ظاهر", "English": "🎨 3. Material & Visuals"},
    "exp_print_est": {"Persian": "⚙️ ۴. پارامترهای اسلایسر و پرینت", "English": "⚙️ 4. Slicer & Print Parameters"},

    "style_label": {"Persian": "سبک گلدان", "English": "Vase Style"},
    "styles": {
        "Persian": ["قطره‌ای کلاسیک (Classic Droplet)", "مدرن استوانه‌ای (Modern Pill)"],
        "English": ["Classic Droplet", "Modern Pill"]
    },
    "height": {"Persian": "ارتفاع کل (mm)", "English": "Total Height (mm)"},
    "base_radius": {"Persian": "شعاع کف تخت (mm)", "English": "Flat Base Radius (mm)"},
    "base_thick": {"Persian": "ارتفاع پایه تخت (mm)", "English": "Solid Base Height (mm)"},
    "flutes": {"Persian": "تعداد شیارها", "English": "Number of Flutes"},
    "depth": {"Persian": "عمق شیارها", "English": "Flute Depth"},
    "twist": {"Persian": "پیچش شیارها", "English": "Twist Angle"},

    "enable_cut": {"Persian": "فعال‌سازی برش", "English": "Enable Cut"},
    "cut_plane": {"Persian": "صفحه برش", "English": "Cut Plane"},
    "cut_pos": {"Persian": "موقعیت برش (mm)", "English": "Cut Position (mm)"},
    "keep_part": {"Persian": "بخش نگه‌داشته شده", "English": "Keep Section"},

    "mat_preset": {"Persian": "جنس / رنگ فیلامنت", "English": "Filament Material"},
    "mat_options": ["PLA Silk Gold", "PLA Silk Silver", "PLA Matte Black", "PLA Glossy White", "PETG Translucent Red", "PLA Terracotta / Clay"],

    "infill_density": {"Persian": "تراکم اینفیل (Infill %)", "English": "Infill Density (%)"},
    "wall_loops": {"Persian": "تعداد دیواره‌ها (Wall Loops)", "English": "Wall Loops"},
    "print_speed": {"Persian": "سرعت پرینت (mm/s)", "English": "Print Speed (mm/s)"},
    "filament_price": {"Persian": "قیمت هر کیلو فیلامنت ($)", "English": "Price per kg Filament ($)"},

    "view_label": {"Persian": "نمای دوربین", "English": "Camera View"},
    "views": {
        "Persian": ["نمای ایزومتریک (Isometric)", "نمای روبرو (Front)", "نمای زیر / کف (Bottom View)", "نمای ۴۵ درجه (45° Angle)"],
        "English": ["Isometric", "Front View", "Bottom View", "45° Angle"]
    },
    "show_bbox": {"Persian": "نمایش گیج و ابعاد روی مدل (Caliper)", "English": "Show Caliper Box"},
    "download_stl": {"Persian": "📥 دانلود فایل STL", "English": "📥 Download STL File"},
    "download_step": {"Persian": "📐 دانلود فایل STEP (مدل CAD)", "English": "📐 Download STEP File"}
}

st.title(TXT["title"][lang])
st.caption(TXT["subtitle"][lang])

with st.sidebar:
    st.header("🎛️ پنل تنظیمات پارامتری")

    with st.expander(TXT["exp_geometry"][lang], expanded=True):
        selected_style = st.selectbox(TXT["style_label"][lang], TXT["styles"][lang])
        height = st.slider(TXT["height"][lang], 80, 300, 160)
        base_r = st.slider(TXT["base_radius"][lang], 25, 80, 45)
        base_t = st.slider(TXT["base_thick"][lang], 3.0, 15.0, 5.0)
        frequency = st.slider(TXT["flutes"][lang], 10, 80, 36)
        amplitude = st.slider(TXT["depth"][lang], 0.0, 10.0, 3.5)
        twist = st.slider(TXT["twist"][lang], 0.0, 10.0, 0.0)

    with st.expander(TXT["exp_cut"][lang], expanded=False):
        enable_split = st.checkbox(TXT["enable_cut"][lang], value=False)
        plane_type = "XY (افقی - Z)" if lang == "Persian" else "XY (Horizontal - Z)"
        cut_offset = 0.0
        keep_positive = True

        if enable_split:
            plane_type = st.selectbox(
                TXT["cut_plane"][lang],
                ["XY (افقی - Z)", "YZ (عمودی - X)", "ZX (عمودی - Y)"] if lang == "Persian" else ["XY (Horizontal - Z)", "YZ (Vertical - X)", "ZX (Vertical - Y)"]
            )
            
            if "XY" in plane_type:
                cut_offset = st.slider(TXT["cut_pos"][lang], 5.0, float(height - 10), float(height / 2))
                keep_options = ["بخش بالایی (Upper +Z)", "بخش پایینی (Lower -Z)"] if lang == "Persian" else ["Upper (+Z)", "Lower (-Z)"]
            elif "YZ" in plane_type:
                max_r = float(base_r + 40)
                cut_offset = st.slider(TXT["cut_pos"][lang], -max_r, max_r, 0.0)
                keep_options = ["بخش راست (Right +X)", "بخش چپ (Left -X)"] if lang == "Persian" else ["Right (+X)", "Left (-X)"]
            else:
                max_r = float(base_r + 40)
                cut_offset = st.slider(TXT["cut_pos"][lang], -max_r, max_r, 0.0)
                keep_options = ["بخش جلو (Front +Y)", "بخش عقب (Back -Y)"] if lang == "Persian" else ["Front (+Y)", "Back (-Y)"]
                
            keep_choice = st.radio(TXT["keep_part"][lang], keep_options)
            keep_positive = True if ("Upper" in keep_choice or "راست" in keep_choice or "Right" in keep_choice or "جلو" in keep_choice or "Front" in keep_choice or "بالایی" in keep_choice) else False

    with st.expander(TXT["exp_material"][lang], expanded=False):
        selected_material = st.selectbox(TXT["mat_preset"][lang], TXT["mat_options"])
        selected_view = st.selectbox(TXT["view_label"][lang], TXT["views"][lang])

    with st.expander(TXT["exp_print_est"][lang], expanded=False):
        infill = st.slider(TXT["infill_density"][lang], 0, 100, 15)
        wall_count = st.slider(TXT["wall_loops"][lang], 1, 6, 2)
        p_speed = st.slider(TXT["print_speed"][lang], 30, 300, 80)
        fil_cost = st.number_input(TXT["filament_price"][lang], value=20.0, step=1.0)

def get_material_properties(mat_name):
    materials = {
        "PLA Silk Gold": {"color": "#D4AF37", "roughness": 0.15, "specular": 0.8, "fresnel": 0.5, "density": 1.24},
        "PLA Silk Silver": {"color": "#C0C0C0", "roughness": 0.15, "specular": 0.9, "fresnel": 0.6, "density": 1.24},
        "PLA Matte Black": {"color": "#222222", "roughness": 0.8, "specular": 0.1, "fresnel": 0.05, "density": 1.24},
        "PLA Glossy White": {"color": "#F5F5F5", "roughness": 0.2, "specular": 0.6, "fresnel": 0.2, "density": 1.24},
        "PETG Translucent Red": {"color": "#E63946", "roughness": 0.3, "specular": 0.7, "fresnel": 0.4, "density": 1.27},
        "PLA Terracotta / Clay": {"color": "#C86D51", "roughness": 0.9, "specular": 0.05, "fresnel": 0.01, "density": 1.30}
    }
    return materials.get(mat_name, materials["PLA Silk Gold"])

def export_to_step(mesh):
    verts = mesh.vertices
    faces = mesh.faces
    header = "ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('Parametric Vase Model'), '2;1');\nFILE_NAME('vase.stp', '2026-01-01', ('User'), ('Studio'), 'Trimesh STEP', 'Streamlit', '');\nFILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));\nENDSEC;\nDATA;\n#10 = APPLICATION_CONTEXT('3D design');\n#11 = APPLICATION_PROTOCOL_DEFINITION('international standard', 'config_control_design', 2000, #10);\n"
    body = []
    entity_id = 20
    pt_map = {}
    for idx, v in enumerate(verts):
        pid = entity_id
        body.append(f"#{pid} = CARTESIAN_POINT('', ({v[0]:.4f}, {v[1]:.4f}, {v[2]:.4f}));")
        pt_map[idx] = pid
        entity_id += 1
    face_ids = []
    for f in faces:
        p1, p2, p3 = pt_map[f[0]], pt_map[f[1]], pt_map[f[2]]
        v1_id, v2_id, v3_id = entity_id, entity_id + 1, entity_id + 2
        body.append(f"#{v1_id} = VERTEX_POINT('', #{p1});\n#{v2_id} = VERTEX_POINT('', #{p2});\n#{v3_id} = VERTEX_POINT('', #{p3});")
        entity_id += 3
        f_id = entity_id
        body.append(f"#{f_id} = TRIANGULATION_FACE('', (#{v1_id}, #{v2_id}, #{v3_id}));")
        face_ids.append(f"#{f_id}")
        entity_id += 1
    footer = f"\n#{entity_id} = CLOSED_SHELL('', ({','.join(face_ids)}));\nENDSEC;\nEND-ISO-10303-21;\n"
    return (header + "\n".join(body) + footer).encode('utf-8')

@st.cache_data
def generate_vase(h, base_radius_val, base_thickness, freq, amp, tw, style_idx, do_split, plane_str, offset_val, keep_pos):
    num_height_steps = 120
    num_theta_steps = 120

    z_vals = np.linspace(base_thickness, h, num_height_steps)
    theta_vals = np.linspace(0, 2 * np.pi, num_theta_steps, endpoint=False)
    Z_grid, Theta_grid = np.meshgrid(z_vals, theta_vals, indexing='ij')

    t = (Z_grid - base_thickness) / (h - base_thickness)
    fade_in = np.clip(t * 8.0, 0.0, 1.0)

    if style_idx == 0:
        shape_factor = np.sin(np.pi * t**0.8) - 0.3 * t**2 + 0.15 * (t**4)
        base_outer_r = base_radius_val + 35 * shape_factor
    else:
        profile = np.sin(np.pi * t)**0.3
        base_outer_r = base_radius_val + 25 * profile

    wave = amp * np.sin(freq * Theta_grid + tw * t) * fade_in
    R_outer = base_outer_r + wave

    X_out = R_outer * np.cos(Theta_grid)
    Y_out = R_outer * np.sin(Theta_grid)

    vertices = []
    faces = []

    for i in range(num_height_steps):
        for j in range(num_theta_steps):
            vertices.append([X_out[i, j], Y_out[i, j], Z_grid[i, j]])

    for i in range(num_height_steps - 1):
        for j in range(num_theta_steps):
            j_next = (j + 1) % num_theta_steps
            p1 = i * num_theta_steps + j
            p2 = i * num_theta_steps + j_next
            p3 = (i + 1) * num_theta_steps + j_next
            p4 = (i + 1) * num_theta_steps + j
            faces.append([p1, p2, p3])
            faces.append([p1, p3, p4])

    bottom_flat_start = len(vertices)
    for j in range(num_theta_steps):
        ang = theta_vals[j]
        x_b = base_radius_val * np.cos(ang)
        y_b = base_radius_val * np.sin(ang)
        vertices.append([x_b, y_b, 0.0])

    for j in range(num_theta_steps):
        j_next = (j + 1) % num_theta_steps
        p_bot1 = bottom_flat_start + j
        p_bot2 = bottom_flat_start + j_next
        p_top1 = j
        p_top2 = j_next
        faces.append([p_bot1, p_bot2, p_top2])
        faces.append([p_bot1, p_top2, p_top1])

    grid_rings = 12
    ring_start_indices = []

    for r_i in range(grid_rings + 1):
        r_frac = r_i / grid_rings
        current_r = base_radius_val * r_frac
        ring_start = len(vertices)
        ring_start_indices.append(ring_start)

        for j in range(num_theta_steps):
            ang = theta_vals[j]
            x_p = current_r * np.cos(ang)
            y_p = current_r * np.sin(ang)
            vertices.append([x_p, y_p, 0.0])

    for r_i in range(grid_rings):
        prev_start = ring_start_indices[r_i]
        curr_start = ring_start_indices[r_i + 1]

        for j in range(num_theta_steps):
            j_next = (j + 1) % num_theta_steps
            p1 = prev_start + j
            p2 = prev_start + j_next
            p3 = curr_start + j_next
            p4 = curr_start + j
            faces.append([p1, p2, p3])
            faces.append([p1, p3, p4])

    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
    mesh.fill_holes()
    trimesh.repair.fix_normals(mesh)

    if do_split:
        if "XY" in plane_str:
            plane_origin = [0, 0, offset_val]
            plane_normal = [0, 0, 1 if keep_pos else -1]
        elif "YZ" in plane_str:
            plane_origin = [offset_val, 0, 0]
            plane_normal = [1 if keep_pos else -1, 0, 0]
        else:
            plane_origin = [0, offset_val, 0]
            plane_normal = [0, 1 if keep_pos else -1, 0]

        mesh = mesh.slice_plane(plane_origin, plane_normal, cap_surface=True)

    stl_data = mesh.export(file_type='stl')
    step_data = export_to_step(mesh)

    return mesh, stl_data, step_data

style_index = 0 if ("Droplet" in selected_style or "قطره‌ای" in selected_style) else 1

mesh, stl_bytes, step_bytes = generate_vase(
    height, base_r, base_t, frequency, amplitude, twist, style_index,
    enable_split, plane_type, cut_offset, keep_positive
)

mat_props = get_material_properties(selected_material)
vol_cm3 = mesh.volume / 1000.0 if mesh.volume > 0 else 120.0

effective_volume = vol_cm3 * (0.3 + 0.7 * (infill / 100.0)) * (1 + 0.1 * (wall_count - 2))
weight_grams = effective_volume * mat_props["density"]
estimated_cost = (weight_grams / 1000.0) * fil_cost

estimated_time_mins = (height / 0.2) * (base_r * 2 / p_speed) * 0.8
hrs = int(estimated_time_mins // 60)
mins = int(estimated_time_mins % 60)

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("📦 حجم هندسی", f"{vol_cm3:.1f} cm³")
with m2:
    st.metric("⚖️ وزن تقریبی", f"{weight_grams:.1f} g")
with m3:
    st.metric("⏱️ زمان پرینت", f"{hrs}h {mins}m")
with m4:
    st.metric("💰 هزینه متریال", f"${estimated_cost:.2f}")
with m5:
    st.metric("📐 ابعاد کل (Z)", f"{height} mm")

show_caliper_box = st.checkbox(TXT["show_bbox"][lang], value=True)

camera_preset = dict(eye=dict(x=1.4, y=1.4, z=1.2), center=dict(x=0, y=0, z=0))
if "Front" in selected_view or "روبرو" in selected_view:
    camera_preset = dict(eye=dict(x=0, y=2.2, z=0.1), center=dict(x=0, y=0, z=0))
elif "Bottom" in selected_view or "کف" in selected_view:
    camera_preset = dict(eye=dict(x=0, y=0.01, z=-2.2), center=dict(x=0, y=0, z=0))
elif "45°" in selected_view or "۴۵" in selected_view:
    camera_preset = dict(eye=dict(x=1.2, y=1.2, z=0.5), center=dict(x=0, y=0, z=0))

verts = mesh.vertices
faces = mesh.faces
min_bounds, max_bounds = mesh.bounds

fig = go.Figure()

fig.add_trace(go.Mesh3d(
    x=verts[:, 0], y=verts[:, 1], z=verts[:, 2],
    i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
    color=mat_props["color"],
    flatshading=False,
    lighting=dict(
        ambient=0.35,
        diffuse=0.8,
        fresnel=mat_props["fresnel"],
        specular=mat_props["specular"],
        roughness=mat_props["roughness"]
    ),
    name="Vase"
))

if show_caliper_box:
    x0, y0, z0 = min_bounds
    x1, y1, z1 = max_bounds
    box_lines_x = [x0, x1, x1, x0, x0, x0, x1, x1, x0, x0, x1, x1, x1, x1, x0, x0]
    box_lines_y = [y0, y0, y1, y1, y0, y0, y0, y1, y1, y0, y0, y0, y1, y1, y1, y1]
    box_lines_z = [z0, z0, z0, z0, z0, z1, z1, z1, z1, z1, z1, z0, z0, z1, z1, z0]

    fig.add_trace(go.Scatter3d(
        x=box_lines_x, y=box_lines_y, z=box_lines_z,
        mode='lines',
        line=dict(color='#FF3366', width=3, dash='dash'),
        name="Caliper Box"
    ))

fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data',
        camera=camera_preset,
        dragmode='orbit'
    ),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0, r=0, b=0, t=0)
)

st.plotly_chart(
    fig, 
    use_container_width=True, 
    config={
        'scrollZoom': True,
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d']
    }
)

d_col1, d_col2 = st.columns(2)
with d_col1:
    st.download_button(
        label=TXT["download_stl"][lang],
        data=stl_bytes,
        file_name="flat_base_parametric_vase.stl",
        mime="application/octet-stream"
    )
with d_col2:
    st.download_button(
        label=TXT["download_step"][lang],
        data=step_bytes,
        file_name="flat_base_parametric_vase.stp",
        mime="application/octet-stream"
    )
