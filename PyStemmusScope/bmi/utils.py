"""Utilities for the STEMMUS_SCOPE Basic Model Interface."""
import numpy as np


INAPPLICABLE_GRID_METHOD_MSG = (
    "This grid method is not implmented for the STEMMUS_SCOPE BMI because the model is"
    "\non a rectilinear grid."
)


class InapplicableBmiMethods:
    """Holds methods that are not applicable for STEMMUS_SCOPE's rectilinear grid."""

    def get_grid_spacing(self, grid: int, spacing: np.ndarray) -> np.ndarray:
        """Get distance between nodes of the computational grid."""
        raise NotImplementedError(INAPPLICABLE_GRID_METHOD_MSG)

    def get_grid_origin(self, grid: int, origin: np.ndarray) -> np.ndarray:
        """Get coordinates for the lower-left corner of the computational grid."""
        raise NotImplementedError(INAPPLICABLE_GRID_METHOD_MSG)

    def get_var_location(self, name: str) -> str:
        """Get the grid element type that the a given variable is defined on."""
        raise NotImplementedError(INAPPLICABLE_GRID_METHOD_MSG)

    def get_grid_node_count(self, grid: int) -> int:
        """Get the number of nodes in the grid."""
        raise NotImplementedError(INAPPLICABLE_GRID_METHOD_MSG)

    def get_grid_edge_count(self, grid: int) -> int:
        """Get the number of edges in the grid."""
        raise NotImplementedError(INAPPLICABLE_GRID_METHOD_MSG)

    def get_grid_face_count(self, grid: int) -> int:
        """Get the number of faces in the grid."""
        raise NotImplementedError(INAPPLICABLE_GRID_METHOD_MSG)

    def get_grid_edge_nodes(self, grid: int, edge_nodes: np.ndarray) -> np.ndarray:
        """Get the edge-node connectivity."""
        raise NotImplementedError(INAPPLICABLE_GRID_METHOD_MSG)

    def get_grid_face_edges(self, grid: int, face_edges: np.ndarray) -> np.ndarray:
        """Get the face-edge connectivity."""
        raise NotImplementedError(INAPPLICABLE_GRID_METHOD_MSG)

    def get_grid_face_nodes(self, grid: int, face_nodes: np.ndarray) -> np.ndarray:
        """Get the face-node connectivity."""
        raise NotImplementedError(INAPPLICABLE_GRID_METHOD_MSG)

    def get_grid_nodes_per_face(
        self, grid: int, nodes_per_face: np.ndarray
    ) -> np.ndarray:
        """Get the number of nodes for each face."""
        raise NotImplementedError(INAPPLICABLE_GRID_METHOD_MSG)
