#!/usr/bin/env lua
local function get_script_dir()
	local path = string.sub(debug.getinfo(1, "S").source, 2)
	-- Handle both forward slash (Unix) and backslash (Windows)
	local dir = path:match("(.*[/\\])")
	if not dir then
		dir = "./"  -- current directory if no path separator found
	end
	return dir
end

local script_dir = get_script_dir()
local hypercurve_path = "/Users/j/Documents/hypercurve/hypercurve-master"
package.cpath = package.cpath .. ";" .. hypercurve_path .. "/build/bin/?.dylib;"

local hc = require("lua_hypercurve")

-- deterministic seed: pass as arg, else fall back to a fixed default
local seed = tonumber(arg[1]) or tonumber(os.date("36%m%d%I%M%S"))
--math.randomseed(seed)

FT_SIZE = 8192
SAMPLE_RATE = 48000

local function rand_float(min_val, max_val)
	return min_val + math.random() * (max_val - min_val)
end

local curve_specs = {
	cissoid_curve = function() return { rand_float(0.5125, 1.5) } end,
	diocles_curve = function() return { rand_float(0.5125, 1.5) } end,
	cubic_curve = function() return {} end,
	bicorn_curve = function() return {} end,
	catenary_curve = function() return { rand_float(0.05, 1) } end,
	funicular_curve = function() return { rand_float(0.05, 1) } end,
	toxoid_curve = function() return {} end,
	duplicatrix_cubic_curve = function() return {} end,
	kiss_curve = function() return {} end,
	mouth_curve = function() return {} end,
	gaussian_curve = function() return { rand_float(0.2, 2.0), rand_float(0.2, 2.0) } end,
	gauss_curve = function() return { rand_float(0.2, 2.0), rand_float(0.2, 2.0) } end,
	tightrope_walker_curve = function() return { rand_float(0.5, 2.0), rand_float(0.05, 0.5) } end,
	hanning_curve = function() return {} end,
	hamming_curve = function() return {} end,
	blackman_curve = function() return {} end,
	cubic_bezier_curve = function() return { rand_float(0, 1), rand_float(0, 1), rand_float(0, 1), rand_float(0, 1) } end,
	quadratic_bezier_curve = function() return { rand_float(0, 1), rand_float(0, 1) } end,
	cubic_spline_curve = function() return {} end,
	catmull_rom_curve = function() return {} end,
	power_curve = function() return { rand_float(0.3, 4.0) } end,
	exponential_curve = function() return { rand_float(0.5, 4.0) } end,
	logarithmic_curve = function() return { rand_float(0.5, 4.0) } end,
	polynomial_curve = function() return { rand_float(0.5, 4.0) } end,
}

-- collect ease_* names, then SORT before inserting anywhere —
-- pairs() order is unspecified and will silently break determinism otherwise
--[[ local ease_names = {}
for key, _ in pairs(hc) do
	if key:match("^ease_") and key:match("_curve$") then
		table.insert(ease_names, key)
	end
end
table.sort(ease_names)
-- ease_*_curve: "Exponent must be > to 1" — 1 is a legal rand_float(1, 3) result
for _, name in ipairs(ease_names) do
	curve_specs[name] = function() return { rand_float(1.15, 4) } end
end ]]

-- same fix here: sort spec names before building curve_pool
local spec_names = {}
for name, _ in pairs(curve_specs) do
	table.insert(spec_names, name)
end
table.sort(spec_names)

local curve_pool = {}
for _, name in ipairs(spec_names) do
	if hc[name] then
		table.insert(curve_pool, name)
	end
end

local function build_curve_base(name)
	local constructor = hc[name]
	local args = curve_specs[name]()

	local ok, result = pcall(constructor, table.unpack(args))
	if ok then
		return result
	end

	local ok_fallback, result_fallback = pcall(constructor)
	if ok_fallback then
		return result_fallback
	end

	return nil
end

local function shuffle(t)
	for i = #t, 2, -1 do
		local j = math.random(i)
		t[i], t[j] = t[j], t[i]
	end
	return t
end

local function build_random_segments()
	local segment_count = math.random(24, 32)


	local xs = {}
	for i = 1, segment_count do
		xs[i] = (i % math.random(2, 8) == 0) and .5+math.random()/2 or math.random()/9
	end

	local ys = {}
	if segment_count > 3 then
		for i = 1, segment_count-3 do
			ys[i] = (i % math.random(2, 8) == 0) and .5+math.random()/2 or 0
		end
	end

	table.insert(ys, 1)
	ys = shuffle(ys)
	table.insert(ys, 1, 0)
	table.insert(ys, #ys+1, 0)

	local segments = {}
	for i = 1, segment_count do
		local x_dest = xs[i]
		local y_dest = ys[i]
		local curve_name = curve_pool[math.random(#curve_pool)]
		print(curve_name)
		local curve_base = build_curve_base(curve_name) or hc.cubic_curve()

		table.insert(segments, hc.segment(x_dest, y_dest, curve_base))
	end

	return segments
end

local function save_wav(filename, data, sr)
	local bytes_per_sample = 3
	local channels = 1
	local block_align = channels * bytes_per_sample
	local byte_rate = sr * block_align
	local bit_depth = 24
	local max_val = 8388607

	local f = io.open(filename, "wb")
	if not f then error('file not valid') end
	f:write("RIFF" .. string.pack("<I4", 36 + #data * bytes_per_sample) .. "WAVEfmt " ..
				string.pack("<I4I2I2I4I4I2I2", 16, 1, channels, sr, byte_rate, block_align, bit_depth) ..
				"data" .. string.pack("<I4", #data * bytes_per_sample))

	for i = 1, #data do
		local s = math.max(-1, math.min(1, data[i]))
		local sample = math.floor(s * max_val + 0.5)
		local packed = string.pack("<i4", sample)
		f:write(packed:sub(1, 3))
	end

	f:close()
	print("Saved: " .. filename)
end

local function make(max_attempts)
	max_attempts = max_attempts or 500

	for attempt = 1, max_attempts do
		local segments = build_random_segments()
		local crv = hc.hypercurve(FT_SIZE, 0, segments)
		local samples = crv:get_samples()

		-- Check all conditions
		local valid = true

		-- Condition 1: Must start with 0
		if samples[1] > (1/8) then
			valid = false
		end

		-- Condition 2: Must end near 0 (within 1/8)
		if samples[#samples] > (1/4) then
			valid = false
		end

		-- Condition 3: Must have at least one value == 1
		local has_one = false
		for _, v in ipairs(samples) do
			if v == 1 then
				has_one = true
				break
			end
		end
		if not has_one then
			valid = false
		end

		if valid then
			return samples, crv  -- Success!
		end
	end

	error("Failed to generate valid waveform after " .. max_attempts .. " attempts")
end

local samples, crv = make()

local out_stem = string.format("%s/%d%s", script_dir, seed, string.lower(tostring(os.date("%p"))))

local fill = true
local is_waveform = true
local draw_grid = false
local invert_color = true

crv:write_as_png(out_stem .. ".png", is_waveform, fill, draw_grid, invert_color)
save_wav(out_stem .. ".wav", samples, SAMPLE_RATE)

print("Done! seed=" .. seed)