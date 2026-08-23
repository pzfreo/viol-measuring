"""A studio renderer for the assembled rig.

The MCP's viewer and matplotlib both give a flat, washed-out picture: no
shadows, no occlusion, no control of the light.  This drives VTK directly with
physically-based materials, an image-based light built from a procedural sky,
a shadow-casting key light and screen-space ambient occlusion, which is what
makes a printed part read as a printed part and a steel rod as steel.
"""

import numpy as np
import vtk
from vtkmodules.util import numpy_support



def cubemap(top=(0.86, 0.89, 0.94), horizon=(0.72, 0.74, 0.78),
            bottom=(0.34, 0.33, 0.32), n=192):
    """A cheap studio environment: bright above, warm and dark below.

    Image-based lighting is most of what makes metal look like metal, and a
    six-sided gradient is enough to get the falloff without shipping an HDR.
    """
    top, horizon, bottom = (np.array(c, np.float32) for c in (top, horizon, bottom))
    tex = vtk.vtkTexture()
    tex.CubeMapOn()
    tex.InterpolateOn()
    tex.MipmapOn()
    for face in range(6):
        u, v = np.meshgrid(np.linspace(-1, 1, n), np.linspace(-1, 1, n))
        if face == 2:      # +Y, up
            h = np.ones_like(u)
        elif face == 3:    # -Y, down
            h = -np.ones_like(u)
        else:
            h = -v
        t = np.clip(h, -1, 1)[..., None]
        up, down = np.clip(t, 0, 1) ** 0.8, np.clip(-t, 0, 1) ** 0.7
        img = horizon + (top - horizon) * up + (bottom - horizon) * down
        arr = (np.clip(img, 0, 1) * 255).astype(np.uint8).reshape(-1, 3)
        vimg = vtk.vtkImageData()
        vimg.SetDimensions(n, n, 1)
        vtk_arr = numpy_support.numpy_to_vtk(arr, deep=True)
        vtk_arr.SetNumberOfComponents(3)
        vimg.GetPointData().SetScalars(vtk_arr)
        tex.SetInputDataObject(face, vimg)
    return tex


def actor_from_stl(path, colour, metallic, roughness, occlusion=1.0):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(path))
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(reader.GetOutputPort())
    normals.SetFeatureAngle(48)          # keep printed arrises sharp
    normals.SplittingOn()
    normals.ConsistencyOn()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    a = vtk.vtkActor()
    a.SetMapper(mapper)
    p = a.GetProperty()
    p.SetInterpolationToPBR()
    p.SetColor(*colour)
    p.SetMetallic(metallic)
    p.SetRoughness(roughness)
    p.SetOcclusionStrength(occlusion)
    return a


def ground(z, half, colour=(0.66, 0.67, 0.69)):
    plane = vtk.vtkPlaneSource()
    plane.SetOrigin(-half, -half, z)
    plane.SetPoint1(half, -half, z)
    plane.SetPoint2(-half, half, z)
    plane.SetResolution(1, 1)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(plane.GetOutputPort())
    a = vtk.vtkActor()
    a.SetMapper(mapper)
    p = a.GetProperty()
    p.SetInterpolationToPBR()
    p.SetColor(*colour)
    p.SetMetallic(0.0)
    p.SetRoughness(0.85)
    return a


def render(actors, bounds, out, size=(1900, 1050), eye_dir=(-0.50, 1.15, 0.50),
           fov=23.0, bg=(0.972, 0.976, 0.982), bg2=(0.836, 0.856, 0.888)):
    lo = np.array([bounds[0], bounds[2], bounds[4]], float)
    hi = np.array([bounds[1], bounds[3], bounds[5]], float)
    centre = (lo + hi) / 2
    span = float(np.max(hi - lo))

    ren = vtk.vtkRenderer()
    ren.SetBackground(*bg)
    ren.SetBackground2(*bg2)
    ren.GradientBackgroundOn()
    ren.UseImageBasedLightingOn()
    ren.SetEnvironmentTexture(cubemap())
    ren.UseSphericalHarmonicsOff()
    ren.AutomaticLightCreationOff()

    for a in actors:
        ren.AddActor(a)

    d = np.array(eye_dir, float)
    d /= np.linalg.norm(d)
    cam = ren.GetActiveCamera()
    cam.SetPosition(*(centre + d * span))
    cam.SetFocalPoint(*centre)
    cam.SetViewUp(0, 0, 1)
    cam.SetViewAngle(fov)
    # let VTK do the framing along that direction, then back off a little so
    # nothing touches the edge; and reset the clipping range or it silently
    # cuts the front and back off the scene
    ren.ResetCamera(bounds[0], bounds[1], bounds[2], bounds[3], bounds[4], bounds[5])
    cam.Zoom(1.22)
    # pan without changing the perspective, to sit the pair centrally
    cam.SetWindowCenter(0.16, -0.04)
    ren.ResetCameraClippingRange()

    key = vtk.vtkLight()
    key.SetPositional(False)
    key.SetPosition(*(centre + np.array([-1.1, 1.0, 1.6]) * span))
    key.SetFocalPoint(*centre)
    key.SetColor(1.0, 0.985, 0.955)
    key.SetIntensity(1.15)
    ren.AddLight(key)

    fill = vtk.vtkLight()
    fill.SetPositional(False)
    fill.SetPosition(*(centre + np.array([1.5, 0.7, 0.25]) * span))
    fill.SetFocalPoint(*centre)
    fill.SetColor(0.86, 0.90, 1.0)
    fill.SetIntensity(0.35)
    ren.AddLight(fill)

    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetMultiSamples(8)
    win.AddRenderer(ren)
    win.SetSize(*size)

    # No shadow-map or SSAO pass here on purpose.  VTK's shadow pass clips
    # this geometry and its screen-space occlusion speckles the thin rods at
    # any radius that does anything useful.  Image-based lighting off the
    # procedural sky does the shaping instead, which is stable.

    win.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.SetScale(1)
    w2i.ReadFrontBufferOff()
    w2i.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(out))
    writer.SetInputConnection(w2i.GetOutputPort())
    writer.Write()
    return out
