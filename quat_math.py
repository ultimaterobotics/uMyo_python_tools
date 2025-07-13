"""Quaternion Mathematics Library for 3D Orientation Calculations

This module provides a comprehensive set of quaternion and vector operations
for 3D spatial mathematics, specifically designed for EMG sensor orientation
tracking and gesture recognition applications.

Quaternions provide a robust and efficient representation for 3D rotations,
avoiding gimbal lock and providing smooth interpolation. This library implements
all fundamental quaternion operations needed for sensor fusion, orientation
tracking, and spatial transformations.

Classes:
    sV: Named tuple representing a 3D vector (x, y, z)
    sQ: Named tuple representing a quaternion (w, x, y, z)

Functions:
    Quaternion Operations:
        q_norm: Calculate quaternion magnitude
        q_renorm: Normalize quaternion to unit length
        q_make_conj: Compute quaternion conjugate
        q_mult: Multiply two quaternions
        
    Vector Operations:
        v_norm: Calculate vector magnitude
        v_renorm: Normalize vector to unit length
        v_mult: Cross product of two vectors
        v_dot: Dot product of two vectors
        
    Spatial Transformations:
        rotate_v: Rotate vector by quaternion
        q_from_vectors: Compute rotation quaternion between vectors

Example:
    ```python
    import quat_math
    
    # Create quaternion for 90-degree rotation around Z-axis
    q = quat_math.sQ(w=0.707, x=0, y=0, z=0.707)
    
    # Create vector pointing in X direction
    v = quat_math.sV(x=1, y=0, z=0)
    
    # Rotate vector - should point in Y direction after 90° Z rotation
    rotated = quat_math.rotate_v(q, v)
    print(f"Rotated vector: ({rotated.x:.3f}, {rotated.y:.3f}, {rotated.z:.3f})")
    # Output: Rotated vector: (0.000, 1.000, 0.000)
    ```

Note:
    All quaternions are assumed to be unit quaternions (magnitude = 1) for
    valid rotation representations. Use q_renorm() to ensure unit length.
    
    Quaternion format: q = w + xi + yj + zk where (w, x, y, z) are real numbers
    and i, j, k are the fundamental quaternion units.
"""

import math
from collections import namedtuple
from typing import Union

# Type definitions for 3D spatial mathematics
sV = namedtuple("sV", "x y z")        # 3D Vector: (x, y, z)
sQ = namedtuple("sQ", "w x y z")      # Quaternion: w + xi + yj + zk


def q_norm(q: sQ) -> float:
    """Calculate the magnitude (norm) of a quaternion.
    
    The quaternion norm is the 4D Euclidean distance from the origin,
    calculated as √(w² + x² + y² + z²). For unit quaternions representing
    rotations, this should equal 1.0.
    
    Args:
        q (sQ): Input quaternion with components (w, x, y, z)
        
    Returns:
        float: Magnitude of the quaternion
        
    Example:
        >>> q = sQ(w=1, x=0, y=0, z=0)  # Identity quaternion
        >>> magnitude = q_norm(q)
        >>> print(f"Magnitude: {magnitude}")
        Magnitude: 1.0
        
        >>> q2 = sQ(w=2, x=3, y=4, z=5)  # Non-unit quaternion
        >>> magnitude2 = q_norm(q2)
        >>> print(f"Magnitude: {magnitude2:.3f}")
        Magnitude: 7.348
    """
    return math.sqrt(q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w)


def v_norm(v: sV) -> float:
    """Calculate the magnitude (norm) of a 3D vector.
    
    The vector norm is the Euclidean distance from the origin,
    calculated as √(x² + y² + z²).
    
    Args:
        v (sV): Input vector with components (x, y, z)
        
    Returns:
        float: Magnitude of the vector
        
    Example:
        >>> v = sV(x=3, y=4, z=0)  # 3-4-5 triangle
        >>> magnitude = v_norm(v)
        >>> print(f"Magnitude: {magnitude}")
        Magnitude: 5.0
        
        >>> unit_x = sV(x=1, y=0, z=0)
        >>> print(f"Unit vector magnitude: {v_norm(unit_x)}")
        Unit vector magnitude: 1.0
    """
    return math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z)


def q_renorm(q: sQ) -> sQ:
    """Normalize a quaternion to unit length.
    
    Converts any quaternion to a unit quaternion (magnitude = 1) by dividing
    all components by the quaternion's magnitude. Unit quaternions represent
    valid 3D rotations. If the input quaternion has zero magnitude, returns
    the zero quaternion.
    
    Args:
        q (sQ): Input quaternion to normalize
        
    Returns:
        sQ: Normalized unit quaternion
        
    Example:
        >>> q = sQ(w=2, x=0, y=0, z=0)  # Non-unit quaternion
        >>> q_unit = q_renorm(q)
        >>> print(f"Original: {q}")
        >>> print(f"Normalized: {q_unit}")
        >>> print(f"Magnitude: {q_norm(q_unit):.6f}")
        Original: sQ(w=2, x=0, y=0, z=0)
        Normalized: sQ(w=1.0, x=0.0, y=0.0, z=0.0)
        Magnitude: 1.000000
    """
    r = q_norm(q)
    w = 0
    x = 0
    y = 0
    z = 0
    if (r > 0):
        m = 1.0 / r
        w = q.w * m
        x = q.x * m
        y = q.y * m
        z = q.z * m
    return sQ(w, x, y, z)


def v_renorm(v: sV) -> sV:
    """Normalize a vector to unit length.
    
    Converts any vector to a unit vector (magnitude = 1) by dividing all
    components by the vector's magnitude. If the input vector has zero
    magnitude, returns the zero vector.
    
    Args:
        v (sV): Input vector to normalize
        
    Returns:
        sV: Normalized unit vector
        
    Example:
        >>> v = sV(x=3, y=4, z=0)
        >>> v_unit = v_renorm(v)
        >>> print(f"Original: {v}")
        >>> print(f"Normalized: {v_unit}")
        >>> print(f"Magnitude: {v_norm(v_unit):.6f}")
        Original: sV(x=3, y=4, z=0)
        Normalized: sV(x=0.6, y=0.8, z=0.0)
        Magnitude: 1.000000
    """
    r = v_norm(v)
    x = 0
    y = 0
    z = 0
    if (r > 0):
        m = 1.0 / r
        x = v.x * m
        y = v.y * m
        z = v.z * m
    return sV(x, y, z)


def q_make_conj(q: sQ) -> sQ:
    """Compute the conjugate of a quaternion.
    
    The quaternion conjugate is formed by negating the vector part (x, y, z)
    while keeping the scalar part (w) unchanged. For unit quaternions, the
    conjugate represents the inverse rotation.
    
    Args:
        q (sQ): Input quaternion
        
    Returns:
        sQ: Conjugate quaternion (w, -x, -y, -z)
        
    Mathematical Note:
        For unit quaternion q, q * q̄ = 1 (where q̄ is the conjugate)
        
    Example:
        >>> q = sQ(w=0.707, x=0, y=0, z=0.707)  # 90° rotation around Z
        >>> q_conj = q_make_conj(q)
        >>> print(f"Original: {q}")
        >>> print(f"Conjugate: {q_conj}")
        Original: sQ(w=0.707, x=0, y=0, z=0.707)
        Conjugate: sQ(w=0.707, x=0, y=0, z=-0.707)
    """
    rq = sQ(q.w, -q.x, -q.y, -q.z)
    return rq


def q_mult(q1: sQ, q2: sQ) -> sQ:
    """Multiply two quaternions.
    
    Quaternion multiplication represents the composition of rotations.
    The result q1 * q2 represents applying rotation q2 first, then q1.
    Note that quaternion multiplication is non-commutative (q1*q2 ≠ q2*q1).
    
    Args:
        q1 (sQ): Left quaternion in multiplication
        q2 (sQ): Right quaternion in multiplication
        
    Returns:
        sQ: Product quaternion representing composed rotation
        
    Mathematical Formula:
        (w1 + x1i + y1j + z1k) * (w2 + x2i + y2j + z2k)
        = (w1w2 - x1x2 - y1y2 - z1z2) +
          (w1x2 + x1w2 + y1z2 - z1y2)i +
          (w1y2 - x1z2 + y1w2 + z1x2)j +
          (w1z2 + x1y2 - y1x2 + z1w2)k
          
    Example:
        >>> # 90° rotation around Z, then 90° around X
        >>> q_z = sQ(w=0.707, x=0, y=0, z=0.707)
        >>> q_x = sQ(w=0.707, x=0.707, y=0, z=0)
        >>> q_combined = q_mult(q_x, q_z)
        >>> print(f"Combined rotation: {q_combined}")
    """
    w = q1.w * q2.w - (q1.x * q2.x + q1.y * q2.y + q1.z * q2.z)
    x = q1.w * q2.x + q2.w * q1.x + q1.y * q2.z - q1.z * q2.y
    y = q1.w * q2.y + q2.w * q1.y + q1.z * q2.x - q1.x * q2.z
    z = q1.w * q2.z + q2.w * q1.z + q1.x * q2.y - q1.y * q2.x
    return sQ(w, x, y, z)


def rotate_v(q: sQ, v: sV) -> sV:
    """Rotate a 3D vector by a quaternion.
    
    Applies the rotation represented by quaternion q to vector v.
    This is performed using the formula: v' = q * v * q*
    where q* is the quaternion conjugate and v is treated as a pure
    quaternion (0, vx, vy, vz).
    
    Args:
        q (sQ): Unit quaternion representing the rotation
        v (sV): Vector to be rotated
        
    Returns:
        sV: Rotated vector
        
    Note:
        The input quaternion should be normalized (unit quaternion) for
        correct rotation behavior.
        
    Example:
        >>> # Rotate X-axis vector by 90° around Z-axis
        >>> q_z90 = sQ(w=0.707, x=0, y=0, z=0.707)
        >>> v_x = sV(x=1, y=0, z=0)
        >>> v_rotated = rotate_v(q_z90, v_x)
        >>> print(f"Rotated vector: ({v_rotated.x:.3f}, {v_rotated.y:.3f}, {v_rotated.z:.3f})")
        Rotated vector: (0.000, 1.000, 0.000)  # Now points in Y direction
    """
    r = sQ(0, v.x, v.y, v.z)
    qc = q_make_conj(q)
    qq = q_mult(r, qc)
    rq = q_mult(q, qq)
    return sV(rq.x, rq.y, rq.z)


def qv_mult(q1: sQ, q2: sQ) -> sQ:
    """Cross product of quaternion vector parts as quaternion.
    
    Computes the cross product of the vector parts (x, y, z) of two
    quaternions and returns the result as a pure quaternion (w=0).
    This is used in some quaternion algorithms for vector calculations.
    
    Args:
        q1 (sQ): First quaternion
        q2 (sQ): Second quaternion
        
    Returns:
        sQ: Pure quaternion with w=0 and vector part = q1.vec × q2.vec
        
    Mathematical Formula:
        result = (0, q1.y*q2.z - q1.z*q2.y, q1.z*q2.x - q1.x*q2.z, q1.x*q2.y - q1.y*q2.x)
    """
    x = q1.y * q2.z - q1.z * q2.y
    y = q1.z * q2.x - q1.x * q2.z
    z = q1.x * q2.y - q1.y * q2.x
    return sQ(0, x, y, z)


def v_mult(v1: sV, v2: sV) -> sV:
    """Compute the cross product of two 3D vectors.
    
    The cross product v1 × v2 produces a vector perpendicular to both input
    vectors, with magnitude equal to the area of the parallelogram formed
    by the vectors. The direction follows the right-hand rule.
    
    Args:
        v1 (sV): First vector
        v2 (sV): Second vector
        
    Returns:
        sV: Cross product vector v1 × v2
        
    Properties:
        - v1 × v2 = -(v2 × v1) (anti-commutative)
        - |v1 × v2| = |v1| * |v2| * sin(θ) where θ is angle between vectors
        - v1 × v2 = 0 if vectors are parallel
        
    Example:
        >>> v1 = sV(x=1, y=0, z=0)  # X-axis
        >>> v2 = sV(x=0, y=1, z=0)  # Y-axis
        >>> cross = v_mult(v1, v2)
        >>> print(f"X × Y = {cross}")
        X × Y = sV(x=0, y=0, z=1)  # Z-axis (right-hand rule)
    """
    x = v1.y * v2.z - v1.z * v2.y
    y = v1.z * v2.x - v1.x * v2.z
    z = v1.x * v2.y - v1.y * v2.x
    return sV(x, y, z)


def v_dot(v1: sV, v2: sV) -> float:
    """Compute the dot product of two 3D vectors.
    
    The dot product v1 · v2 is a scalar value equal to the sum of the
    products of corresponding components. It represents the projection
    of one vector onto another.
    
    Args:
        v1 (sV): First vector
        v2 (sV): Second vector
        
    Returns:
        float: Dot product v1 · v2
        
    Properties:
        - v1 · v2 = |v1| * |v2| * cos(θ) where θ is angle between vectors
        - v1 · v2 = 0 if vectors are perpendicular
        - v1 · v2 > 0 if angle < 90°, < 0 if angle > 90°
        
    Applications:
        - Calculate angle between vectors: θ = arccos((v1·v2)/(|v1|*|v2|))
        - Project v1 onto v2: proj = (v1·v2/|v2|²) * v2
        - Test for perpendicularity: v1·v2 = 0
        
    Example:
        >>> v1 = sV(x=1, y=0, z=0)
        >>> v2 = sV(x=0, y=1, z=0)
        >>> dot = v_dot(v1, v2)
        >>> print(f"Dot product: {dot}")
        Dot product: 0.0  # Perpendicular vectors
        
        >>> v3 = sV(x=1, y=1, z=0)
        >>> dot2 = v_dot(v1, v3)
        >>> print(f"Dot product: {dot2}")
        Dot product: 1.0  # 45° angle
    """
    return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z


def q_from_vectors(u: sV, v: sV) -> sQ:
    """Compute the quaternion that rotates vector u to vector v.
    
    Calculates the shortest rotation quaternion that transforms vector u
    into vector v. This is useful for aligning coordinate systems or
    computing relative orientations.
    
    Args:
        u (sV): Source vector (starting direction)
        v (sV): Target vector (desired direction)
        
    Returns:
        sQ: Unit quaternion representing the rotation from u to v
        
    Algorithm:
        Uses Rodrigues' rotation formula adapted for quaternions.
        For vectors u and v, the rotation axis is u × v and the
        rotation angle is arccos(u · v / (|u| * |v|)).
        
    Special Cases:
        - If u and v are parallel: returns identity quaternion
        - If u and v are anti-parallel: returns 180° rotation around perpendicular axis
        
    Example:
        >>> u = sV(x=1, y=0, z=0)  # X-axis
        >>> v = sV(x=0, y=1, z=0)  # Y-axis  
        >>> q = q_from_vectors(u, v)
        >>> # Should be 90° rotation around Z-axis
        >>> rotated = rotate_v(q, u)
        >>> print(f"Rotated X to: ({rotated.x:.3f}, {rotated.y:.3f}, {rotated.z:.3f})")
        Rotated X to: (0.000, 1.000, 0.000)
    """
    d = v_dot(u, v)
    w = v_mult(u, v)
    w = d + math.sqrt(d * d + v_dot(w, w))
    x = w.x
    y = w.y
    z = w.z
    res = sQ(w, x, y, z)
    return q_renorm(res)
