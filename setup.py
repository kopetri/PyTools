import setuptools

setuptools.setup(
    name='PyTools',
    version='0.0.1',
    description='collection of usefull stuff',
    url='https://github.com/kopetri/PyTools.git',
    author='Sebastian Hartwig',
    author_email='sebastianhartwig@gmx.net',
    maintainer='Sebastian Hartwig',
    maintainer_email='sebastianhartwig@gmx.net',
    packages=setuptools.find_packages(),
    install_requires=['numpy', 'opencv-python', 'pyrr', 'PyOpenGL', 'PyQt5']
)
